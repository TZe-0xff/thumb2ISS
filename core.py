import struct
import re
import binascii
import importlib
import logging
import glob
import core_routines
from register import Register

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class EndOfExecutionException(Exception):
    pass

class ProgramStatus:
    def __init__(self):
        self.N = False
        self.Z = False
        self.C = False
        self.V = False
        self.Q = False
        self.GE = [False] * 4
        self.ITsteps = 0
        self.ITcond = None
    

    def update(self, flags):
        self.N = flags.get('N', self.N)
        self.Z = flags.get('Z', self.Z)
        self.C = flags.get('C', self.C)
        self.V = flags.get('V', self.V)
        self.Q = flags.get('Q', self.Q)

    def __str__(self):
        ge_bits = ''.join(str(int(v)) for v in self.GE)
        return f'N: {int(self.N)} | Z: {int(self.Z)} | C: {int(self.C)} | V: {int(self.V)} | Q: {int(self.Q)} | GE: {ge_bits[::-1]}'

class Core(core_routines.Api, metaclass=Singleton):
    def __init__(self, log_root=None, profile=False):
        self.initializeRegisters()
        self.reg_num = {f'{p}{i}':i for i in range(16) for p in 'rR'}
        self.reg_num.update({'SB':0, 'sb':9, 'SL':10, 'sl':10, 'FP':11, 'fp':11, 'IP': 12, 'ip':12, 'SP':13, 'sp':13, 'LR':14, 'lr':14, 'PC':15, 'pc':15})
        self.bytes_to_Uint = ['', '<B', '<H', '', '<L']
        if log_root is None:
            self.log = logging.getLogger('Core')
        else:
            self.log = log_root.getChild('Core')
        self.instructions = {}
        self.profile = profile
        if self.profile:
            self.matched_patterns = {}
            self.exec_called = {}
            self.exec_by_mnem = {}
        from instructions._all import patterns
        self.instructions = patterns


        if self.profile:
            for mnem in self.instructions:
                self.matched_patterns[mnem] = {pat[0].pattern:0 for pat in self.instructions[mnem]}
                self.exec_by_mnem[mnem] = []
                for _, action, _ in self.instructions[mnem]:
                    if action.__name__+'_exec' not in self.exec_by_mnem[mnem]:
                        self.exec_by_mnem[mnem].append(action.__name__+'_exec')
                    self.exec_called[action.__name__+'_exec'] = 0

    def initializeRegisters(self):
        self.R = {i:self.Field(0) for i in range(16)}
        self.R[14] = self.Field(0xffffffff) # initial LR
        self.APSR = ProgramStatus()
        self.pc_updated = False
        self.break_reached = False

    def readR(self, reg_id):
        if reg_id < 15:
            return self.R[reg_id]
        else:
            return self.PC

    @property
    def PC(self):
        return self.R[15] + 4 # In Thumb state: the value of the PC is the address of the current instruction plus 4 bytes

    @PC.setter
    def PC(self, value):
        self.pc_updated = True
        self.R[15] = value

    @property
    def SP(self):
        return self.R[13]

    @SP.setter
    def SP(self, value):
        self.R[13] = value

    @property
    def LR(self):
        return self.R[14]

    @LR.setter
    def LR(self, value):
        self.R[14] = value

    def configure(self, pc, sp, mem):
        self.initializeRegisters()
        self.memory = mem
        self.R[15] = self.Field(pc & 0xfffffffe)
        self.R[13] = self.Field(sp)

    def getPC(self):
        return self.UInt(self.R[15])

    def getLR(self):
        return self.UInt(self.R[14])

    def incPC(self, step):
        if not self.pc_updated:
            #raise(Exception('#### PC increment'))
            self.R[15] = self.R[15] + step
            if self.APSR.ITsteps > 0:
                self.APSR.ITsteps -= 1
                if self.APSR.ITsteps == 0:
                    self.APSR.ITcond = None
        else:
            self.pc_updated = False
            self.APSR.ITsteps = 0
            self.APSR.ITcond = None
        return self.break_reached


    def showRegisters(self, indent=0):
        for i in range(13):
            if i%4 == 0 and indent:
                print(' '*indent, end='')
            print(f'r{i}: {hex(self.UInt(self.R[i]))}', end='  ')
            if i%4 == 3:
                print('')
        print(f'sp: {hex(self.UInt(self.R[13]))}', end='  ')
        print(f'lr: {hex(self.UInt(self.R[14]))}', end='  ')
        print(f'pc: {hex(self.UInt(self.R[15]))}')
        print(' '*indent, self.APSR, sep='')

    def getExec(self, mnem, full_assembly, expected_pc):
        m = None
        if mnem.upper() not in self.instructions:
            if mnem.upper() == 'LDMIA' or mnem.upper() == 'STMIA':
                mnem = mnem[:-2]
            elif mnem.upper().startswith('IT'):
                mnem = 'IT'
            else:
                # try to remove trailing condition
                for legal_cond in ['EQ', 'NE', 'CS', 'CC', 'MI', 'PL', 'VS', 'VC', 'HI', 'LS', 'GE', 'LT', 'GT', 'LE']:
                    if mnem.upper().endswith(legal_cond):
                        mnem = mnem[:-2]
                        break
        for pat, action, bitdiffs in self.instructions.get(mnem.upper(), []):
            m = pat.match(full_assembly)
            if m is not None:
                break
        if m is not None:
            if self.profile:
                self.matched_patterns[mnem.upper()][pat.pattern] += 1
            instr_exec = action(self, m, bitdiffs)
            def mnem_exec():
                try:
                    assert(expected_pc == self.UInt(self.R[15]))
                except:
                    raise Exception(f'{full_assembly} Expected PC to be {hex(expected_pc)} but was {hex(self.UInt(self.R[15]))}')
                if self.profile:
                    self.exec_called[instr_exec.__name__] += 1
                instr_exec()
            return mnem_exec

        if mnem.upper() not in ['CPSIE', 'CPSID', 'DMB', 'DSB', 'ISB', 'WFE', 'WFI', 'SEV', 'SVC']:
            print(self.instructions.get(mnem.upper(), []))
            raise Exception(f'Unmanaged {mnem} : {full_assembly}')
        def debug_exec():
            self.log.warning(f'Unsupported {mnem} executed as NOP')
        return debug_exec

    def Exit(self):
        raise EndOfExecutionException(f'End of execution')
    
    def Field(self, value, msb=31, lsb=0):
        mask = (0xffffffff >> (31 - msb + lsb)) << lsb
        if type(value) != int:
            value = self.UInt(value)
        val = (value & mask) >> lsb

        reg_res = Register(struct.pack('<L', val))
        reg_res._msb = msb - lsb
        return reg_res
        

