import struct
import re
import binascii
import importlib
import logging
import glob

class Register:
    def __init__(self, initial_value):
        if type(initial_value) == Register:
            self.ival = initial_value.ival
            self.bval = initial_value.bval
        elif type(initial_value) == bytes:
            self.bval = initial_value
            self.ival = struct.unpack('<l', initial_value)[0]
        elif type(initial_value) == str:
            self.ival = int(initial_value, 0)
            self.bval = struct.pack('<l', self.ival)
        else:
            self.ival = int(initial_value)
            self.bval = struct.pack('<l', self.ival)

    @staticmethod
    def __get_ival(other):
        if type(other) == Register:
            other_ival = other.ival
        elif type(other) == bytes:
            other_ival = struct.unpack('<l', other)[0]
        elif type(other) == str:
            other_ival = int(other, 0)
        else:
            other_ival = int(other)
        return other_ival


    def __add__(self, other): # +
        return Register(self.ival + self.__get_ival(other))

    def __sub__(self, other): # –
        return Register(self.ival - self.__get_ival(other))

    def __and__(self, other): # &
        return Register(self.ival & self.__get_ival(other))

    def __or__(self, other): # |
        return Register(self.ival | self.__get_ival(other))

    def __xor__(self, other): # ^
        return Register(self.ival ^ self.__get_ival(other))


    def __eq__(self, other): # ==
        return self.ival == self.__get_ival(other)

    def __ne__(self, other): # !=
        return self.ival != self.__get_ival(other)

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

class Core:
    def __init__(self):
        self.R = {i:self.Field(0) for i in range(16)}
        self.R[14] = self.Field(0xffffffff) # initial LR
        self.reg_num = {f'{p}{i}':i for i in range(16) for p in 'rR'}
        self.reg_num.update({'FP':11, 'fp':11, 'IP': 12, 'ip':12, 'SP':13, 'sp':13, 'LR':14, 'lr':14, 'PC':15, 'pc':15})
        self.APSR = ProgramStatus()
        self.bytes_to_Uint = ['', '<B', '<H', '', '<L']
        self.log = logging.getLogger('Core')
        
        self.instructions = {}
        for instr in glob.glob('instructions/[a-z]*.py'):
            instr_module = instr.replace('\\','.').replace('.py','')
            self.instructions.update(importlib.import_module(instr_module).patterns)

    @property
    def PC(self):
        return self.R[15] + 4 # In Thumb state: the value of the PC is the address of the current instruction plus 4 bytes

    @PC.setter
    def PC(self, value):
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
        self.memory = mem
        self.R[15] = self.Field(pc & 0xfffffffe)
        self.R[13] = self.Field(sp)

    def getPC(self):
        return self.UInt(self.R[15])

    def incPC(self, step):
        self.R[15] = self.R[15] + step
        if self.APSR.ITsteps > 0:
            self.APSR.ITsteps -= 1
            if self.APSR.ITsteps == 0:
                self.APSR.ITcond = None

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

    def getExec(self, mnem, args, expected_pc):
        m = None
        for pat, action, bitdiffs in self.instructions.get(mnem.upper(), []):
            m = pat.match(f'{mnem} {args}')
            if m is not None:
                break
        if m is not None:
            instr_exec = action(self, m, bitdiffs)
            def mnem_exec():
                assert(expected_pc == self.UInt(self.R[15]))
                instr_exec()
            return mnem_exec
        def debug_exec():
            self.log.warning(f'Unsupported {mnem} executed as NOP')
        return debug_exec


    
    def Field(self, value, msb=31, lsb=0):
        mask = (0xffffffff >> (31 - msb + lsb)) << lsb
        val = (value & mask) >> lsb
        return Register(struct.pack('<L', val))

    def UInt(self, value):
        if type(value) == Register:
            value = value.bval
        elif value == '0' or value == '1':
            pass
        elif type(value) == str:
            value = struct.pack('<l', int(value, 0))
        elif type(value) == int:
            value = struct.pack('<l', value)
        if type(value) == bytes:
            return struct.unpack('<L', value)[0]
        return int(value)
        

    def SInt(self, value):
        if type(value) == Register:
            return value.ival
        elif value == '0' or value == '1':
            pass
        elif type(value) == str:
            value = struct.pack('<l', int(value, 0))
        elif type(value) == int:
            value = struct.pack('<l', value)
        if type(value) == bytes:
            return struct.unpack('<l', value)[0]
        return int(value)

    def Bit(self, value, bit_pos=31):
        if type(value) == bytes or type(value) == Register:
            return (self.UInt(value) & (1 << bit_pos)) != 0
        elif type(value) == str:
            value = int(value, 0)
        return (value & (1 << bit_pos)) != 0

    def IsZero(self, value):
        if type(value) == Register:
            return (value.ival == 0)
        elif type(value) == bytes:
            return (self.UInt(value) == 0)
        return (int(value) == 0)

    def IsZeroBit(self, value):
        return self.IsZero(value)

    def NOT(self, value):
        if type(value) == Register:
            print(f'NOT({hex(value.ival)}) = {hex(~value.ival)}')
            return (~value.ival)
        elif type(value) == bytes:
            return ~self.UInt(value)
        elif type(value) == bool:
            return not value
        return ~int(value)


    def InITBlock(self):
        return self.APSR.ITcond is not None

    def ConditionPassed(self, cond):
        return True

    def ReadMemU(self, address, size):
        assert(size in [1,2,4])
        try:
            byte_seq = b''.join(self.memory[i] for i in range(address.ival, address.ival + size))
        except KeyError:
            raise Exception(f'Illegal memory access between {hex(address.ival)} and {hex(address.ival + size - 1)}')

        # load as unsigned
        value = struct.unpack(self.bytes_to_Uint[size], byte_seq)[0]
        self.log.info(f'Read {size} bytes as unsigned from {hex(address.ival)} : {hex(value)}')
        return Register(struct.pack('<L', value))

    def Align(self, reg_value, boundary):
        address = self.UInt(reg_value) & (-boundary)
        return Register(struct.pack('<L', address))

    def Shift(self, value, srtype, amount, carry_in):
        (result, _) = self.Shift_C(value, srtype, amount, carry_in)
        return result

    def Shift_C(self, value, srtype, amount, carry_in):
        if amount == 0:
            (result, carry_out) = (value, carry_in)
        else:
            if srtype == 'LSL':
                (result, carry_out) = self.LSL_C(value, amount)
            elif srtype == 'LSR':
                pass #(result, carry_out) = self.LSR_C(value, amount)
            elif srtype == 'ASR':
                pass #(result, carry_out) = self.ASR_C(value, amount)
            elif srtype == 'ROR':
                pass #(result, carry_out) = self.ROR_C(value, amount)
            elif srtype == 'RRX':
                pass #(result, carry_out) = self.RRX_C(value, carry_in)

        return (result, carry_out)

    def LSL_C(self, x, shift):
        extended_x = self.UInt(x) << shift;
        result = self.Field(extended_x, 32-1, 0)
        carry_out = self.Bit(extended_x, 32)
        return (result, carry_out)


    def AddWithCarry(self, x, y, carry_in):
        unsigned_sum = self.UInt(x) + self.UInt(y) + self.UInt(carry_in)
        signed_sum = self.SInt(x) + self.SInt(y) + self.UInt(carry_in);
        result = self.Field(unsigned_sum, 31, 0) # same value as signed_sum<N-1:0>
        nzcv = {'N': self.Bit(result, 31),
                'Z' : self.IsZero(result),
                'C' : self.UInt(result) != unsigned_sum,
                'V' : self.SInt(result) != signed_sum
                }
        carry_out = nzcv['C']
        self.log.debug(f'Carry is {carry_out} because result {hex(self.UInt(result))} vs {hex(unsigned_sum)}')
        return (result, nzcv)
        

