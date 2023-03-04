from register import Register
import struct
import semihosting


class Api():


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
        self.log.debug(f'Carry is {carry_out} because result {hex(self.UInt(result))} vs {hex(unsigned_sum)}')
        return (result, nzcv)

    def ALUException(self, address):
        raise Exception(f'ALUException @ {hex(self.UInt(address))}')

    def ALUWritePC(self, address):
        self.BranchWritePC(address, 'INDIR')

    def UInt(self, value, highValue=None):
        if type(value) == Register:
            value = value.bval
        elif value == '0' or value == '1':
            value = int(value)
        elif type(value) == str:
            value = struct.pack('<l', int(value, 0))
        elif type(value) == int:
            value = struct.pack('<l', value)

        if type(value) == bytes:
            value = struct.unpack('<L', value)[0]

        if highValue is not None:
            highValue = self.UInt(highValue)
            combo = struct.pack('<LL', value, highValue)
            value = struct.unpack('<Q', combo)[0]
        return value
        

    def SInt(self, value, highValue=None):
        if type(value) == Register:
            return value.ival
        elif value == '0' or value == '1':
            value = int(value)
        elif type(value) == str:
            value = struct.pack('<l', int(value, 0))
        elif type(value) == int:
            value = struct.pack('<l', value)

        if type(value) == bytes:
            value = struct.unpack('<l', value)[0]

        if highValue is not None:
            highValue = self.UInt(highValue)
            combo = struct.pack('<lL', value, highValue)
            value = struct.unpack('<q', combo)[0]

        return value

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

    def ZeroExtend(self, candidate, bitsize, msb=None, lsb=None):
        assert(bitsize==32)
        in_c = candidate
        if type(candidate) is str and ('0' in candidate or '1' in candidate):
            value = int(candidate, 2)
        elif msb is not None:
            candidate = self.Field(candidate, msb, lsb)
            value = self.UInt(candidate)
        else:
            value = self.UInt(candidate)

        self.log.debug(f'ZeroExtended {self.UInt(in_c)} to {hex(value)}')
        return self.Field(value)

    def ZeroExtendSubField(self, candidate, msb, lsb, bitsize):
        return self.ZeroExtend(candidate, bitsize, msb, lsb)

    def SignExtend(self, candidate, bitsize, msb=None, lsb=None):
        assert(bitsize==32)
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
            value = value | (0xFFFFFFFF << candidate._msb)

        self.log.debug(f'SignExtended {self.UInt(in_c)} to {hex(value)}')
        return self.Field(value)

    def SignExtendSubField(self, candidate, msb, lsb, bitsize):
        return self.SignExtend(candidate, bitsize, msb, lsb)



    def NOT(self, value):
        if type(value) == Register:
            self.log.debug(f'NOT({hex(value.ival)}) = {hex(~value.ival)}')
            return (~value.ival)
        elif type(value) == bytes:
            return ~self.UInt(value)
        elif type(value) == bool:
            return not value
        return ~int(value)

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

    def ReadMemS(self, address, size):
        return self.ReadMemU(address, size)

    def ReadMemA(self, address, size):
        return self.ReadMemU(address, size)

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

    def WriteMemA(self, address, size, value):
        self.WriteMemU(address, size, value)

    def WriteMemS(self, address, size, value):
        self.WriteMemU(address, size, value)

    def BranchWritePC(self, targetAddress, branchType):
        if branchType == 'DIRCALL':
            self.LR = self.R[15] + 5
        elif branchType == 'INDCALL':
            self.LR = self.R[15] + 3
        self.log.info(f'Branching to {hex(self.UInt(targetAddress))}' + (f' with link back to {hex(self.UInt(self.LR))}' if branchType.endswith('CALL') else ''))
        self.PC = Register(targetAddress & (~1))

    def BXWritePC(self, targetAddress, branchType):
        self.BranchWritePC(targetAddress, branchType)

    def CBWritePC(self, targetAddress):
        self.BranchWritePC(targetAddress, 'DIR')

    def LoadWritePC(self, address):
        self.BXWritePC(address, 'INDIR');

    def SoftwareBreakpoint(self, value):
        value = self.UInt(value)
        if value == 0xab:
            #semihosting
            semihosting.ExecuteCmd(self)
        else:
            self.log.info(f'Breakpoint #{hex(value)} executed as NOP')

    def Align(self, reg_value, boundary):
        address = self.UInt(reg_value) & (-boundary)
        return Register(struct.pack('<L', address))

    def IsAligned(self, address, size):
        return False #(self.UInt(address) & (size-1)) == 0

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
        

