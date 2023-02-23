import re
import logging
import binascii
import struct
from core import Core

class Architecture:
    CortexM0 = 0
    CortexM0p= 1
    CortexM3 = 2
    CortexM4 = 3
    CortexM23= 4
    CortexM33= 5

class Simulator(object):

    def __init__(self, t_arch=Architecture.CortexM4):
        self.t_arch = t_arch
        self.log = logging.getLogger('Simulator')
        #self.timings_table = timings.load(t_arch)
        self.dis_patt = [
            # Labels
            (re.compile(r'^(?P<address>[\da-f]{8}) <(?P<label>[^>]+)>: *'), 
                lambda m: self.genLbl(m.group('label'), int(m.group('address'), 16))),
            # code
            (re.compile(r'^ +(?P<address>[\da-f]+):\s+(?P<lowWord>[\da-f ]{4})(?: +(?P<higWord>[\da-f]{4}))?\s+(?P<mnem>\w[\w.]+)\s*(?P<args>[^;\n\t]+)?.*'),
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
        self.log.getChild('genIsn').debug(f'Get Execution for <{mnemonic}> ({full_assembly})')
        self.code[address] = (self.core.getExec(mnemonic, full_assembly, address), len(data))

    def genConst(self, address, value_str, data_type):
        self.log.getChild('genConst').debug(f'Creating Constant @{hex(address)} : {value_str}')
        if data_type != '.table':
            chunks = [value_str]
        else:
            chunks = value_str.strip().split(' ')  
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

    def load(self, disassembly, rom_memory, rom_start, ram_memory, ram_start):
        self.labels = {}
        self.memory = {}
        self.code   = {}
        self.core = Core()
        for line in disassembly.splitlines():
            if len(line.strip()) > 0:
                for pat, action in self.dis_patt:
                    m = pat.match(line.lower())
                    if m is not None:
                        action(m)
                        break
        self.memory.update({rom_start+i : rom_memory[i:i+1] for i in range(len(rom_memory))})
        self.memory.update({ram_start+i : ram_memory[i:i+1] for i in range(len(ram_memory))})

        if '__vectors' in self.labels:
            vector_table = self.labels['__vectors']
        elif '__vector_table' in self.labels:
            vector_table = self.labels['__vector_table']
        else:
            print('__vectors symbol missing')
            return False
        # get initial sp & inital pc from vector table
        byte_seq = b''.join(self.memory[i] for i in range(vector_table, vector_table + 8))
        initial_sp, initial_pc = struct.unpack('<LL', byte_seq)
        self.core.configure(initial_pc, initial_sp, self.memory)
        return True

    def step(self):
        ex, pc_step = self.code[self.core.getPC()]
        ex()
        self.core.incPC(pc_step)

if __name__ == '__main__':
    from itertools import groupby
    from intelhex import IntelHex
    import re,sys

    dis_str = open('Hello.log', 'r').read()

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


    ih = IntelHex()
    ih.loadhex('Hello.hex')

    rom_memory = ih.gets(ih.minaddr(), len(ih))

    logging.basicConfig(filename='debug.log', filemode='w', level=logging.DEBUG)
    logging.getLogger('Core').addHandler(logging.StreamHandler(sys.stdout))
    logging.getLogger('Mnem').addHandler(logging.StreamHandler(sys.stdout))
    s = Simulator()
    if s.load(dis_str, rom_memory, ih.minaddr(), ram_memory, ram_start):
        address_ranges = [[v for _,v in g] for _,g in groupby(enumerate(sorted(s.memory.keys())), lambda x:x[0]-x[1])]

        for crange in address_ranges:
            print(f'Memory range : {hex(min(crange))} - {hex(max(crange))}')

        s.core.showRegisters()
        for _ in range(70):
            s.step()
            s.core.showRegisters()
    #print(' '.join(  + list()))
