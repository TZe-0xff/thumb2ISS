import click
import logging
from itertools import groupby
from intelhex import IntelHex
import re,sys,time,os
from sim import Simulator, EndOfExecutionException

@click.command()
@click.argument('elf_file', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, default=False, help='Launch with debugger CLI')
@click.option('-c', '--cpu', type=click.Choice(['M0', 'M0+', 'M3', 'M4', 'M23', 'M33'], case_sensitive=False), default='M4', help='Tune target (supported instructions, cycles)')
@click.option('-l', '--log', type=click.File('w'), help='Full debug log in target file')
@click.option('-v', '--verbose', count=True, help='Tune stderr output verbosity')
@click.option('-t', '--timeout', default=10, show_default=True, help='Simulation timeout (s) (not applicable on debugger)')
def run(elf_file, cpu, debug, log, verbose, timeout):
    ''' Runs ELF_FILE on thumb2 Instruction Set Simulator'''

    if log is not None:
        print(f'log {log}')

    log = logging.getLogger('thumb2ISS')
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logging.getLogger('Mnem').setLevel(logging.WARNING)
    logging.getLogger('thumb2ISS.Sim').setLevel(logging.WARNING)

    log.info(f'Loading elf {elf_file} ...')

    hex_file = os.path.splitext(elf_file)[0] + '.hex'
    dis_file = os.path.splitext(elf_file)[0] + '.dis'
    sec_file = os.path.splitext(elf_file)[0] + '.sec'

    # load disassembly
    with open(dis_file, 'r') as f:
        dis_str = f.read()

    # find RAM area
    with open(sec_file, 'r') as f:
        sec_str = f.read()

    ram_start = 0xFFFFFFFF
    ram_end = 0
    for strt,sz in re.findall(r' ([\da-f]+) +[\da-f]+ +([\da-f]+) +[\da-f]+ +W', sec_str):
        sec_strt = int(strt, 16)
        sec_size = int(sz, 16)
        if sec_strt < ram_start:
            ram_start = sec_strt
        if sec_strt+sec_size > ram_end:
            ram_end = sec_strt + sec_size

    ram_memory = b'\x00' * (ram_end+1-ram_start)

    ih = IntelHex()
    ih.loadhex(hex_file)

    rom_memory = ih.gets(ih.minaddr(), len(ih))

    s = Simulator(log_root=log)
    if s.load(dis_str, rom_memory, ih.minaddr(), ram_memory, ram_start):
        address_ranges = [[v for _,v in g] for _,g in groupby(enumerate(sorted(s.memory.keys())), lambda x:x[0]-x[1])]

        for crange in address_ranges:
            log.info(f'Memory range : {hex(min(crange))} - {hex(max(crange))}')

    if not debug:
        step_cnt = 0
        start_time = time.time()
        time_limit = timeout + start_time if timeout else False
        try:
            while True:
                s.step()
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


if __name__ == '__main__':
    run()