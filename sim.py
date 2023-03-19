import re
import logging
import binascii
import struct
from itertools import groupby
from core import Core, EndOfExecutionException,Singleton

class Architecture:
    CortexM0 = 0
    CortexM0p= 1
    CortexM3 = 2
    CortexM4 = 3
    CortexM23= 4
    CortexM33= 5

class Simulator(object, metaclass=Singleton):

    def __init__(self, t_arch=Architecture.CortexM4, log_root=None):
        self.t_arch = t_arch
        if log_root is not None:
            self.log = log_root.getChild('Sim')
        else:
            self.log = logging.getLogger('Simulator')
        #self.timings_table = timings.load(t_arch)
        self.dis_patt = [
            # Labels
            (re.compile(r'^(?P<address>[\da-f]{8}) <(?P<label>[^>]+)>: *'), 
                lambda m: self.genLbl(m.group('label'), int(m.group('address'), 16))),
            # code
            (re.compile(r'^ +(?P<address>[\da-f]+):\s+(?P<lowWord>[\da-f ]{4})(?: +(?P<higWord>[\da-f]{4}))?\s+(?P<mnem>[a-z][\w.]+)\s*(?P<args>[^;\n\t]+)?.*'),
                lambda m : self.genIsn(int(m.group('address'), 16), m.group('mnem'), m.group('args'), (m.group('lowWord'),m.group('higWord')))),
            # const data
            (re.compile(r'^ +(?P<address>[\da-f]+):\t(?P<value>[\da-f]+)\s+(?P<mnem>\.[\w.]+).*'),
                lambda m: self.genConst(int(m.group('address'), 16), m.group('value'), m.group('mnem'))),
            # const table/string
            (re.compile(r'^ +(?P<address>[\da-f]+):\t(?P<values>(?:[\da-f]{2} ?)+).*?'),
                lambda m: self.genConst(int(m.group('address'), 16), m.group('values'), '.table')),
        ]
        self.mnem_extract = re.compile(r'(?P<mnem>\w+?)(?:[ACEGHLMNPV][CEILQST])?(?:\.[NW])?', re.I)


    def genLbl(self, label, address):
        self.log.getChild('genLbl').debug(f'Creating label <{label}>@{hex(address)}')
        self.labels[label] = address
        self.label_by_address[address] = label

    def genIsn(self, address, mnemonic, args, encoding):
        self.log.getChild('genIsn').debug(f'Creating instruction <{mnemonic}({args})>@{hex(address)}')
        lowWord, highWord = encoding
        data = binascii.unhexlify(lowWord)[::-1]
        if highWord:
            data+= binascii.unhexlify(highWord)[::-1]

        self.log.getChild('genIsn').debug(f'Got {len(data)} from {hex(address)} to {hex(address+len(data)-1)}')

        full_assembly = f'{mnemonic}'
        if args is not None:
            full_assembly+=f' {args}'
        mnemonic = mnemonic.split('.')[0]
        self.log.getChild('genIsn').debug(f'Get Execution for <{mnemonic}> ({full_assembly}) {self.core}')
        self.code[address] = (self.core.getExec(mnemonic, full_assembly, address), len(data))
        self.dis[address] = f'    {full_assembly}'

    def genConst(self, address, value_str, data_type):
        self.log.getChild('genConst').debug(f'Creating Constant @{hex(address)} : {value_str}')
        if data_type != '.table':
            chunks = [value_str]
            self.dis[address] = f'    #{value_str}'
        else:
            chunks = value_str.strip().split(' ')
            self.dis[address] = f'    #{value_str[:16]}'+('...' if len(value_str) > 16 else '')  
        data = b''
        for chk in chunks:
            if len(chk) > 0:
                raw_data = bytes.fromhex(chk)
                if len(raw_data) <= 4:
                    data+= raw_data[::-1]
                else:
                    data+= raw_data
        self.log.getChild('genConst').debug(f'Got {len(data)} from {hex(address)} to {hex(address+len(data)-1)}')
        for i in range(len(data)):
            self.memory[address+i] = data[i:i+1]

    def load(self, disassembly, rom_memory, rom_start, ram_memorys):
        self.labels = {}
        self.label_by_address = {}
        self.memory = {}
        self.code   = {}
        self.dis    = {}
        self.breakpoints = {}
        self.core = Core(self.log)
        
        for line in disassembly.splitlines():
            if len(line.strip()) > 0:
                for pat, action in self.dis_patt:
                    m = pat.match(line.lower())
                    if m is not None:
                        action(m)
                        break
        self.core = None
        self.rom_start = rom_start
        self.memory.update({rom_start+i : rom_memory[i:i+1] for i in range(len(rom_memory))})
        for ram_start, ram_memory in ram_memorys:
            self.memory.update({ram_start+i : ram_memory[i:i+1] for i in range(len(ram_memory))})

        self.address_ranges = [[v for _,v in g] for _,g in groupby(enumerate(sorted(self.memory.keys())), lambda x:x[0]-x[1])]
        self.address_limits = []
        for crange in self.address_ranges:
            self.address_limits += [(min(crange), max(crange))]

        self.reset()
        return True

    def reset(self):
        core = Core(self.log)
        if '__vectors' in self.labels:
            vector_table = self.labels['__vectors']
        elif '__vector_table' in self.labels:
            vector_table = self.labels['__vector_table']
        else:
            #raise Exception('__vectors symbol missing')
            vector_table = self.rom_start
            
        # get initial sp & inital pc from vector table
        byte_seq = b''.join(self.memory[i] for i in range(vector_table, vector_table + 8))
        initial_sp, initial_pc = struct.unpack('<LL', byte_seq)
        core.configure(initial_pc, initial_sp, self.memory)

    def step_in(self):
        core = Core(self.log)
        ex, pc_step = self.code[core.getPC()]
        if ex == 'break':
            # execute original instruction
            ex, pc_step = self.breakpoints[core.getPC()]
        ex()
        core.incPC(pc_step)

    def step_out(self):
        core = Core(self.log)
        # set breakpoint at LR address & run
        self.run_until(core.getLR() & 0xfffffffe)

    def step_over(self):
        core = Core(self.log)
        cur_pc = core.getPC()
        # set breakpoint at PC + inc & run
        _, pc_step = self.code[cur_pc]
        self.run_until(cur_pc+pc_step)

    def run_until(self, address):
        self.addBreakpoint(address)
        self.run()
        self.removeBreakpoint(address)        

    def run(self):
        core = Core(self.log)
        step_cnt = 0
        while True:
            cur_pc = core.getPC()
            ex, pc_step = self.code[cur_pc]
            if ex == 'break':
                if step_cnt > 0: # do not break on first instruction
                    break
                # execute original instruction
                ex, pc_step = self.breakpoints[cur_pc]
            ex()
            core.incPC(pc_step)
            step_cnt+=1


    def getBreakPoints(self):
        return list(self.breakpoints.keys())

    def getSymbols(self):
        return self.labels

    def getSymbol(self, address):
        return self.label_by_address.get(address, None)

    def getRegisters(self):
        core = Core(self.log)
        reg_list = [(f'R{i:<2}', f'0x{core.UInt(core.R[i]):08x}') for i in range(13)]
        reg_list+= [('SP ', f'0x{core.UInt(core.R[13]):08x}')]
        reg_list+= [('LR ', f'0x{core.UInt(core.R[14]):08x}')]
        reg_list+= [('PC ', f'0x{core.UInt(core.R[15]):08x}')]
        return reg_list, str(core.APSR)

    def getDisassemblyAroundPC(self, before, after):
        core = Core(self.log)
        cur_pc = core.getPC()
        lines = [(a, self.dis[a]) for a in range(cur_pc+before*2, cur_pc+after*2, 2) if a in self.dis]
        final_lines = []
        for addr, dis in lines:
            lbl = self.getSymbol(addr)
            if lbl is not None:
                final_lines.append(f'{lbl}:')
            if addr == cur_pc:
                dis = dis[0:2]+'>'+dis[3:]
            final_lines.append(f'{addr:08x} : ' + dis)
        return final_lines

    def isAddressValid(self, address):
        for minaddr,maxaddr in self.address_limits:
            if minaddr <= address <= maxaddr:
                return True
        return False

    def addBreakpoint(self, address):
        if address not in self.breakpoints and address in self.code:
            prev_exec, pc_step = self.code[address]
            # replace by breakpoint 
            self.code[address] = ('break', pc_step)
            self.dis[address] = 'x'+self.dis[address][1:]
            # store breakpoint info 
            self.breakpoints[address] = (prev_exec, pc_step)

    def removeBreakpoint(self, address):
        if address in self.breakpoints:
            prev_exec, pc_step = self.breakpoints[address]
            self.code[address] = (prev_exec, pc_step)
            self.dis[address] = ' '+self.dis[address][1:]
            del self.breakpoints[address]

if __name__ == '__main__':
    from intelhex import IntelHex
    import re,sys

    dis_str = open('Hello.dis', 'r').read()

    # find RAM area
    sec_str = open('Hello.sec', 'r').read()

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

    run_until = 0x2c8

    ih = IntelHex()
    ih.loadhex('Hello.hex')

    rom_memory = ih.gets(ih.minaddr(), len(ih))

    logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)
    #logging.getLogger('Core').addHandler(logging.StreamHandler(sys.stdout))
    #logging.getLogger('Mnem').addHandler(logging.StreamHandler(sys.stdout))
    s = Simulator()
    if s.load(dis_str, rom_memory, ih.minaddr(), [(ram_start, ram_memory)]):
        for minaddr,maxaddr in s.address_limits:
            print(f'Memory range : {hex(minaddr)} - {hex(maxaddr)}')

        try:
            s.run()
        except EndOfExecutionException:
            print('\nSimulation ended by end of execution')
        except KeyboardInterrupt:
            print('\nSimulation ended by cancelation')
    #print(' '.join(  + list()))
