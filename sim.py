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
        for i in range(len(data)):
            self.memory[address+i] = data[i:i+1]

        self.code[address] = (self.core.getExec(mnemonic, args, address+len(data)), len(data))

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

    def load(self, disassembly):
        self.labels = {}
        self.memory = {}
        self.code   = {}
        self.core = Core()
        for line in disassembly:
            for pat, action in self.dis_patt:
                m = pat.match(line.lower())
                if m is not None:
                    action(m)
                    break
        if '__vectors' in self.labels:
            # get initial sp & inital pc from vector table
            byte_seq = b''.join(self.memory[i] for i in range(self.labels['__vectors'], self.labels['__vectors'] + 8))
            initial_sp, initial_pc = struct.unpack('<LL', byte_seq)
            self.core.configure(initial_pc, initial_sp, self.memory)
        return True

    def step(self):
        ex, pc_step = self.code[self.core.getPC()]
        self.core.incPC(pc_step)
        ex()


tst_str = open('dis.log', 'r').read()

logging.basicConfig(filename='debug.log', filemode='w', encoding='utf-8', level=logging.DEBUG)
s = Simulator()
s.load([l for l in tst_str.splitlines() if len(l) > 1])

s.core.showRegisters()
for _ in range(4):
    s.step()
    s.core.showRegisters()
#print(' '.join(  + list()))
