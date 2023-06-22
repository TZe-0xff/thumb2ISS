from .register import Register
import struct
from .semihosting import ExecuteCmd as semihostExecuteCmd


class Api():

    # A 
    def Abs(self, x):
        return abs(x)

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
        self.log.info(f'Carry is {carry_out} because result {hex(self.UInt(result))} vs {hex(unsigned_sum)}')
        return (result, nzcv)

    def Align(self, reg_value, boundary):
        address = self.UInt(reg_value) & (-boundary)
        return Register(struct.pack('<L', address))

    def ALUException(self, address):
        raise Exception(f'ALUException @ {hex(self.UInt(address))}')

    def ALUWritePC(self, address):
        self.BranchWritePC(address, 'INDIR')

    def ASR(self, x, i):
        if shift == 0:
            result = x;
        else:
            (result, _) = self.ASR_C(x, shift);
        return result

    def ASR_C(self, x, shift):
        extended_x = self.SInt(x)
        result = extended_x >> shift
        carry_out = self.Bit(extended_x, shift-1)
        return (result, carry_out)

    # B

    def BigEndian(self, dontcare):
        return False

    def Bit(self, value, bit_pos=31):
        if type(value) == bytes or type(value) == Register:
            return (self.UInt(value) & (1 << bit_pos)) != 0
        elif type(value) == str:
            value = int(value, 0)
        return (value & (1 << bit_pos)) != 0

    def BranchWritePC(self, targetAddress, branchType):
        if branchType == 'DIRCALL':
            self.LR = self.R[15] + 5
        elif branchType == 'INDCALL':
            self.LR = self.R[15] + 3
        self.log.info(f'Branching to {hex(self.UInt(targetAddress))}' + (f' with link back to {hex(self.UInt(self.LR))}' if branchType.endswith('CALL') else ''))
        self.PC = Register(targetAddress & (~1))

    def BXWritePC(self, targetAddress, branchType):
        self.BranchWritePC(targetAddress, branchType)

    # C
    def CallSupervisor(self, dontcare):
        pass

    def CBWritePC(self, targetAddress):
        self.BranchWritePC(targetAddress, 'DIR')

    def CheckForSVCTrap(self, dontcare):
        pass

    def CheckITEnabled(self, dontcare):
        pass

    def ClearExclusiveLocal(self, dontcare):
        pass

    def ConditionPassed(self, cond):
        if cond is None: return True
        cond = cond.upper()
        if cond == 'EQ': return (self.APSR.Z == True)
        if cond == 'NE': return (self.APSR.Z == False)
        if cond == 'CS': return (self.APSR.C == True)
        if cond == 'CC': return (self.APSR.C == False)
        if cond == 'MI': return (self.APSR.N == True)
        if cond == 'PL': return (self.APSR.N == False)
        if cond == 'VS': return (self.APSR.V == True)
        if cond == 'VC': return (self.APSR.V == False)
        if cond == 'HI': return (self.APSR.C == True and self.APSR.Z == False)
        if cond == 'LS': return (self.APSR.C == False or self.APSR.Z == True)
        if cond == 'GE': return (self.APSR.N == self.APSR.V)
        if cond == 'LT': return (self.APSR.N != self.APSR.V)
        if cond == 'GT': return (self.APSR.Z == False and self.APSR.N == self.APSR.V)
        if cond == 'LE': return (self.APSR.Z == True or self.APSR.N != self.APSR.V)
        if cond == 'AL' or cond == '': return True
        raise Exception(f'Illegal condition : {cond}')

    def CountLeadingZeroBits(self, x):
        return 32 - (self.HighestSetBit(x) + 1)

    # D

    # E

    def ExclusiveMonitorsPass(self, address, size):
        return True

    # F G

    # H

    def HighestSetBit(self, x):
        val = self.UInt(x)
        for i in range(31, -1, -1):
            if val & (1 << i):
                return i
        return -1

    # I

    def IsAligned(self, address, size):
        return False #(self.UInt(address) & (size-1)) == 0

    def IsZero(self, value):
        if type(value) == Register:
            return (value.ival == 0)
        elif type(value) == bytes:
            return (self.UInt(value) == 0)
        return (int(value) == 0)

    def IsZeroBit(self, value):
        return self.IsZero(value)

    # J K

    # L

    def LoadWritePC(self, address):
        self.BXWritePC(address, 'INDIR');

    def LowestSetBit(self, x):
        val = self.UInt(x)
        for i in range(32):
            if val & (1 << i):
                return i
        return 32

    def LSL(self, x, shift):
        if shift == 0:
            result = x;
        else:
            (result, _) = self.LSL_C(x, shift);
        return result

    def LSL_C(self, x, shift):
        extended_x = self.UInt(x) << shift;
        result = extended_x & 0xFFFFFFFF
        carry_out = self.Bit(extended_x, 32)
        return (result, carry_out)

    def LSR(self, x, shift):
        if shift == 0:
            result = x;
        else:
            (result, _) = self.LSR_C(x, shift);
        return result

    def LSR_C(self, x, shift):
        extended_x = self.UInt(x)
        result = extended_x >> shift
        carry_out = self.Bit(extended_x, shift-1)
        return (result, carry_out)

    # M

    # N

    def NOT(self, value):
        if type(value) == bool:
            return not value

        full_scale_val = ~self.UInt(value)

        return self.Field(full_scale_val)

    # O

    # P

    def PCStoreValue(self):
        return self.R[15]

    def ProcessorID(self):
        return 0

    # Q

    # R

    def ReadMemA(self, address, size):
        return self.ReadMemU(address, size)
        
    def ReadMemS(self, address, size):
        return self.ReadMemU(address, size)

    def ReadMemU(self, address, size):
        self._load_result += 1
        assert(size in [1,2,4])
        try:
            byte_seq = b''.join(self.memory[i] for i in range(address.ival, address.ival + size))
        except KeyError:
            raise Exception(f'Illegal memory access between {hex(address.ival)} and {hex(address.ival + size - 1)}')

        # load as unsigned
        value = struct.unpack(self.bytes_to_Uint[size], byte_seq)[0]
        self.log.info(f'Read {size} bytes as unsigned from {hex(address.ival)} : {hex(value)}')
        return self.Field(value, msb=8*size-1)

    def ReadSpecReg(self, spec_reg):
        if spec_reg.upper() in ['MSP', 'PSP']:
            return self.SP
        else: # ['APSR', 'IAPSR', 'EAPSR', 'XPSR', 'IPSR', 'EPSR', 'IEPSR', 'PRIMASK', 'BASEPRI', 'BASEPRI_MAX', 'FAULTMASK', 'CONTROL']
            raise Exception('Special registers not implemented')

    def Real(self, x):
        return float(x)

    def ROR(self, x, shift):
        shift = int(shift)
        if shift == 0:
            result = x;
        else:
            (result, _) = self.ROR_C(x, shift);
        return result

    def ROR_C(self, x, shift):
        m = int(shift % 32)
        if m != 0:
            result = self.LSR(x,m) | self.LSL(x,32-m)
        else:
            result = x
        carry_out = self.Bit(result, 31)
        return (result, carry_out)

    def RRX_C(self, x, carry_in):
        val = self.UInt(x) | (int(carry_in) << 32) 
        result = val >> 1
        carry_out = self.Bit(val,0)
        return (result, carry_out);

    def RoundTowardsZero(self, x):
        return int(x) # python float to integer already rounds towards zero

    # S
    def SetBit(self, bit_table, tgt_bit, tgt_value):
        bit_table[int(tgt_bit)] = bool(int(tgt_value))
        return bit_table

        
    def SetExclusiveMonitors(address, size):
        pass

    def SetField(self, source, msb, lsb, value):
        if type(source) == list:
            bits = value[::-1]
            for i in range(len(bits)):
                source[lsb+i] = bool(int(bits[i]))
        else:
            # Register
            mask = (0xffffffff >> (31 - msb + lsb)) << lsb
            source = (source & ~mask) | ((self.UInt(value) << lsb) & mask)
        return source


    def Shift(self, value, srtype, amount, carry_in):
        (result, _) = self.Shift_C(value, srtype, amount, carry_in)
        return result

    def Shift_C(self, value, srtype, amount, carry_in):
        amount = int(amount)
        srtype = srtype.upper()
        if amount == 0 and srtype != 'RRX':
            (result, carry_out) = (value, carry_in)
        else:
            if srtype == 'LSL':
                (result, carry_out) = self.LSL_C(value, amount)
            elif srtype == 'LSR':
                (result, carry_out) = self.LSR_C(value, amount)
            elif srtype == 'ASR':
                (result, carry_out) = self.ASR_C(value, amount)
            elif srtype == 'ROR':
                (result, carry_out) = self.ROR_C(value, amount)
            elif srtype == 'RRX':
                (result, carry_out) = self.RRX_C(value, carry_in)
            else:
                raise Exception(f'Unsupported srtype {srtype}')

        return (result, carry_out)
        
    def SignedSat(self, i, N):
        (result, _) = self.SignedSatQ(i, N)
        return result

    def SignedSatQ(self, i, N):
        N = self.UInt(N)
        result = i
        saturated = False
        if i > 2**(N-1) - 1:
            result = 2**(N-1) - 1
            saturated = True
        elif i < -(2**(N-1)):
            result = -(2**(N-1))
            saturated = True
        else:
            result = i
        return (result, saturated);

    def SignExtend(self, candidate, bitsize, msb=None, lsb=None):

        in_c = candidate
        if type(candidate) is str and ('0' in candidate or '1' in candidate):
            value = int(candidate, 2)
            msb = len(candidate)
            candidate = self.Field(value)
            candidate._msb = msb
        elif msb is not None:
            candidate = self.Field(candidate, msb, lsb)
        elif type(candidate) != Register:
            candidate = self.Field(candidate)

        # get unsigned representation of value
        value = self.UInt(candidate)

        # test sign bit
        sign_bit = value & (1 << candidate._msb)
        if sign_bit:
            # sign extend
            value = value | ((0xFFFFFFFF << candidate._msb) & 0xFFFFFFFF)

        self.log.info(f'SignExtended {self.UInt(in_c)} to {hex(value)}')
        return self.Field(value, msb=bitsize-1)

    def SignExtendSubField(self, candidate, msb, lsb, bitsize):
        return self.SignExtend(candidate, bitsize, msb, lsb)
    
    def SInt(self, value, highValue=None):
        if type(value) == Register:
            value = self.SignExtend(value, 32).ival
        elif value == '0' or value == '1':
            value = int(value)
        elif type(value) == str:
            value = int(value, 0)

        if type(value) == int:
            if value < 0:
                value = struct.pack('<l', value)
            else:
                value = struct.pack('<L', value)

        if type(value) == bytes:
            value = struct.unpack('<l', value)[0]

        if highValue is not None:
            highValue = self.UInt(highValue)
            combo = struct.pack('<lL', value, highValue)
            value = struct.unpack('<q', combo)[0]

        return value

    def SoftwareBreakpoint(self, value):
        value = self.UInt(value)
        if value == 0xab:
            #semihosting
            semihostExecuteCmd(self)
        else:
            self.log.info(f'Breakpoint #{hex(value)} executed as NOP')

    # T

    # U

    def UInt(self, value, highValue=None):
        if type(value) == Register:
            value = value.bval
        elif value == '0' or value == '1':
            value = int(value)
        elif type(value) == str:
            value = int(value, 0)

        if type(value) == int:
            if value < 0:
                if value < -2**31:
                    print(hex(value))
                value = struct.pack('<l', value)
            else:
                value = struct.pack('<L', value)

        if type(value) == bytes:
            value = struct.unpack('<L', value)[0]

        if highValue is not None:
            highValue = self.UInt(highValue)
            combo = struct.pack('<LL', value, highValue)
            value = struct.unpack('<Q', combo)[0]
        return value
        
    def UnsignedSat(self, i, N):
        (result, _) = self.UnsignedSatQ(i, N)
        return result

    def UnsignedSatQ(self, i, N):
        result = i
        N = self.UInt(N)
        saturated = False
        if i > 2**N - 1:
            result = 2**N - 1
            saturated = True
        elif i < 0:
            result = 0
            saturated = True
        else:
            result = i
        return (result, saturated);

    # V

    # W

    def WriteMemA(self, address, size, value):
        self.WriteMemU(address, size, value)

    def WriteMemS(self, address, size, value):
        self.WriteMemU(address, size, value)

    def WriteMemU(self, address, size, value):
        assert(size in [1,2,4])
        value = self.UInt(value)
        self.log.info(f'Write {size} bytes as unsigned to {hex(address.ival)} : {hex(value)}')
        try:
            i=0
            for b in value.to_bytes(size, byteorder='little'):
                self.memory[address.ival+i] = b.to_bytes(1, byteorder='little')
                i+=1
        except KeyError:
            raise Exception(f'Illegal memory access between {hex(address.ival)} and {hex(address.ival + size - 1)}')


    def WriteSpecReg(self, spec_reg, value):
        if spec_reg.upper() in ['MSP', 'PSP']:
            self.SP = value
        else: # ['APSR', 'IAPSR', 'EAPSR', 'XPSR', 'IPSR', 'EPSR', 'IEPSR', 'PRIMASK', 'BASEPRI', 'BASEPRI_MAX', 'FAULTMASK', 'CONTROL']
            raise Exception('Special registers not implemented')

    # X, Y

    # Z

    def ZeroExtend(self, candidate, bitsize, msb=None, lsb=None):
        in_c = candidate
        if type(candidate) is str and ('0' in candidate or '1' in candidate):
            value = int(candidate, 2)
        elif msb is not None:
            candidate = self.Field(candidate, msb, lsb)
            value = self.UInt(candidate)
        else:
            value = self.UInt(candidate)

        return self.Field(value, msb=bitsize-1)

    def ZeroExtendSubField(self, candidate, msb, lsb, bitsize):
        return self.ZeroExtend(candidate, bitsize, msb, lsb)

    def Zeros(self, N):
        return 0





