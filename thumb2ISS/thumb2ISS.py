import click
import logging
from itertools import groupby
from intelhex import IntelHex
import re,sys,time,os,subprocess,tempfile
from .sim import Simulator, EndOfExecutionException, Core

@click.command()
@click.argument('elf_file', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, default=False, help='Launch with debugger CLI')
@click.option('-c', '--cpu', type=click.Choice(['M0', 'M0+', 'M3', 'M4', 'M23', 'M33'], case_sensitive=False), default='M4', help='Tune target (supported instructions, cycles)')
@click.option('-l', '--log', type=click.File('w'), help='Full debug log in target file')
@click.option('-v', '--verbose', count=True, help='Tune stderr output verbosity')
@click.option('-t', '--timeout', default=10, show_default=True, help='Simulation timeout (s) (not applicable on debugger)')
@click.option('-p', '--profile', is_flag=True, default=False, help='Extract statistics about instruction coverage')
def run(elf_file, cpu, debug, log, verbose, timeout, profile):
    ''' Runs ELF_FILE on thumb2 Instruction Set Simulator'''


    if log is not None:
        logging.basicConfig(level=logging.DEBUG, stream=log)
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stderr)
        logging.getLogger('Mnem').setLevel(logging.WARNING)
        logging.getLogger('thumb2ISS.Sim').setLevel(logging.WARNING)

    log = logging.getLogger('thumb2ISS')
    log.info(f'Loading elf {elf_file} ...')

    # extract hex from elf
    base_name = os.path.splitext(os.path.basename(elf_file))[0]
    hex_file = base_name + '.hex'
    if os.path.exists(hex_file):
        dis_file = base_name + '.dis'
        sec_file = base_name + '.sec'
        ih = IntelHex()
        ih.loadhex(hex_file)
        # load disassembly
        with open(dis_file, 'r') as f:
            dis_str = f.read()

        # find RAM area
        with open(sec_file, 'r') as f:
            sec_str = f.read()

        ram_memories = []
        for strt,sz in re.findall(r' ([\da-f]+) +[\da-f]+ +([\da-f]+) +[\da-f]+ +W', sec_str):
            sec_strt = int(strt, 16)
            sec_size = int(sz, 16)
            ram_memories.append((sec_strt, b'\x00' * sec_size))

        rom_memory = ih.gets(ih.minaddr(), len(ih))

        s = Simulator(log_root=log)
        if s.load(dis_str, rom_memory, ih.minaddr(), ram_memories, profile=profile):
            for minaddr,maxaddr in s.address_limits:
                print(f'Memory range : {hex(minaddr)} - {hex(maxaddr)}', file=sys.stderr)

    else:
        with tempfile.TemporaryDirectory() as tmp:
            hex_path = os.path.join(tmp, hex_file)
            subprocess.run(f'arm-none-eabi-objcopy --gap-fill 0xFF -O ihex "{elf_file}" "{hex_path}"', shell=True)

            ih = IntelHex()
            ih.loadhex(hex_path)
        
            # load disassembly
            dis_str = subprocess.check_output(f'arm-none-eabi-objdump.exe -d -z "{elf_file}"')

            # find RAM area
            sec_str = subprocess.check_output(f'arm-none-eabi-readelf.exe -S "{elf_file}"')

            ram_memories = []
            for strt,sz in re.findall(rb' ([\da-f]+) +[\da-f]+ +([\da-f]+) +[\da-f]+ +W', sec_str):
                sec_strt = int(strt, 16)
                sec_size = int(sz, 16)
                ram_memories.append((sec_strt, b'\x00' * sec_size))

            rom_memory = ih.gets(ih.minaddr(), len(ih))

            s = Simulator(log_root=log)
            if s.load(dis_str.decode('ascii'), rom_memory, ih.minaddr(), ram_memories, profile=profile):
                for minaddr,maxaddr in s.address_limits:
                    print(f'Memory range : {hex(minaddr)} - {hex(maxaddr)}', file=sys.stderr)

    if not debug:
        step_cnt = 0
        start_time = time.time()
        time_limit = timeout + start_time if timeout else False
        try:
            while True:
                s.step_in()
                step_cnt+=1
                if step_cnt%100 == 0:
                    if time_limit and time.time() > time_limit:
                        log.info(f'Simulation ended by timeout : {step_cnt} steps simulated in {timeout} s')
                        break
        except EndOfExecutionException:
            elapsed_time = time.time() - start_time
            log.info(f'Simulation ended by end of execution ({step_cnt} steps simulated in {elapsed_time:.3f} s)')
        except KeyboardInterrupt:
            log.info('Simulation ended by cancelation')
    else:
        # starting debugger
        from .debugger import Debugger
        end_of_exec = False
        d = Debugger()
        try:
            d.loop()    
        except EndOfExecutionException:
            end_of_exec = True
            log.info(f'Simulation ended by end of execution')
        except KeyboardInterrupt:
            log.info('Simulation ended by cancelation')

        if not end_of_exec:
            log.info(f'Simulation ended by Debugger exit')

    if profile:
        from collections import defaultdict
        sum_patt = {}
        if os.path.exists('prof_patt_summary.csv'):
            with open('prof_patt_summary.csv') as f:
                next(f)
                for line in f:
                    _,pat,cnt = line.split(';')
                    sum_patt[pat] = int(cnt.strip())
        else:
            sum_patt = defaultdict(lambda:0)

        sum_exec = {}
        if os.path.exists('prof_exec_summary.csv'):
            with open('prof_exec_summary.csv') as f:
                next(f)
                for line in f:
                    _,exc,cnt = line.split(';')
                    sum_exec[exc] = int(cnt.strip())
        else:
            sum_exec = defaultdict(lambda:0)
            
        used_mnems = []
        c = Core()
        with open(f'prof_patt_{base_name}.csv', 'w') as f:
            with open(f'prof_patt_summary.csv', 'w') as s:
                print('Mnemonic;Pattern;Occurences', file=f)
                print('Mnemonic;Pattern;Occurences', file=s)
        
                for mnem in sorted(c.matched_patterns):
                    for pat,cnt in sorted(c.matched_patterns[mnem].items(), key=lambda x:x[0]):
                        print(';'.join([mnem, pat, str(cnt)]), file=f)
                        print(';'.join([mnem, pat, str(cnt+sum_patt[pat])]), file=s)

        
        with open(f'prof_exec_{base_name}.csv', 'w') as f:           
            with open(f'prof_exec_summary.csv', 'w') as s:
                print('Mnemonic;Function;Executed', file=f)
                print('Mnemonic;Function;Executed', file=s)
                for mnem in sorted(c.exec_by_mnem):
                    for exc in sorted(c.exec_by_mnem[mnem]):
                        print(';'.join([mnem, exc, str(c.exec_called[exc])]), file=f)     
                        print(';'.join([mnem, exc, str(c.exec_called[exc]+sum_exec[exc])]), file=s)            

if __name__ == '__main__':
    run()
