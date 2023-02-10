import struct
import re
import binascii


class ProgramStatus:
    def __init__(self):
        self.N = False
        self.Z = False
        self.C = False
        self.V = False
        self.Q = False
        self.GE = [False] * 4

    def update(self, flags):
        print(flags)
        self.N = flags.get('N', self.N)
        self.Z = flags.get('Z', self.Z)
        self.C = flags.get('C', self.C)
        self.V = flags.get('V', self.V)
        self.Q = flags.get('Q', self.Q)

    def __str__(self):
        return f'N: {int(self.N)} | Z: {int(self.Z)} | C: {int(self.C)} | V: {int(self.V)} | Q: {int(self.Q)}'

class Core:
    def __init__(self, pc, sp):
        self.R = {i:self.Field(0) for i in range(13)}
        self.PC = self.Field(pc)
        self.SP = self.Field(sp)
        self.LR = self.Field(0xffffffff)
        self.reg_num = {f'{p}{i}':i for i in range(16) for p in 'rR'}
        self.reg_num.update({'SP':13, 'sp':13, 'LR':14, 'lr':14, 'PC':15, 'pc':15})
        self.APSR = ProgramStatus()

        self.instructions = {
            'ADC' : [
                (re.compile(r'ADC(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)', re.I), self.aarch32_ADC_i_T1_A, {'S':'0'}),
                ],
            'ADCS' : [
                (re.compile(r'ADCS(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)', re.I), self.aarch32_ADC_i_T1_A, {'S':'1'}),
                ],
        }

    def showRegisters(self):
        for i in range(13):
            print(f'r{i}: {binascii.hexlify(self.R[i])}', end='  ')
            if i%4 == 3:
                print('')
        print(f'sp\t{binascii.hexlify(self.SP)}', end='  ')
        print(f'lr\t{binascii.hexlify(self.LR)}', end='  ')
        print(f'pc\t{binascii.hexlify(self.PC)}')
        print(self.APSR)

    def getExec(self, mnem, args, expected_pc):
        for pat, action, bitdiffs in self.instructions.get(mnem.upper(), []):
            m = pat.match(f'{mnem} {args}')
            if m is not None:
                break
        if m is not None:
            instr_exec = action(m, bitdiffs)
            def mnem_exec():
                assert(expected_pc == self.UInt(self.PC))
                instr_exec()
            return mnem_exec
        def debug_exec():
            print(f'Unsupported {mnem} execution')
        return debug_exec


    
    def Field(self, value, msb=31, lsb=0):
        mask = (0xffffffff >> (31 - msb + lsb)) << lsb
        val = (value & mask) >> lsb
        return struct.pack('<L', val)

    def UInt(self, bval):
        if type(bval) == str or type(bval) == int:
            bval = struct.pack('<l', int(bval, 0))
        if type(bval) == bytes:
            return struct.unpack('<L', bval)[0]
        return int(bval)
        

    def SInt(self, bval):
        if type(bval) == str or type(bval) == int:
            bval = struct.pack('<l', int(bval, 0))
        if type(bval) == bytes:
            return struct.unpack('<l', bval)[0]
        return int(bval)

    def Bit(self, value, bit_pos=31):
        if type(value) == bytes:
            return (self.UInt(value) & (1 << bit_pos)) != 0
        return (value & (1 << bit_pos)) != 0

    def IsZero(self, value):
        if type(value) == bytes:
            return (self.UInt(value) == 0)
        return (int(value) == 0)


    def ConditionPassed(self, cond):
        return True


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
        print(self.UInt(x), self.UInt(y))
        signed_sum = self.SInt(x) + self.SInt(y) + self.UInt(carry_in);
        result = self.Field(unsigned_sum, 31, 0) # same value as signed_sum<N-1:0>
        nzcv = {'N': self.Bit(result, 31),
                'Z' : self.IsZero(result),
                'C' : self.UInt(result) != unsigned_sum,
                'V' : self.SInt(result) != signed_sum
                }
        carry_out = nzcv['C']
        print(f'Carry is {carry_out} because result {binascii.hexlify(result)} vs {unsigned_sum}')
        return (result, nzcv)

    #pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
    #ADC(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)
    #pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
    #ADCS(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)
    def aarch32_ADC_i_T1_A(self, regex_match, bitdiffs):
        # decode
        Rd = regex_match.group('Rd')
        Rn = regex_match.group('Rn')
        cond = regex_match.group('c')
        imm32 = regex_match.group('imm32')
        S = bitdiffs.get('S', '0')
        if Rd is None:
            Rd = Rn
        print(f'aarch32_ADC_i_T1_A {Rd}, {Rn}, {cond}, {imm32}, {S}')

        d = self.reg_num[Rd]; n = self.reg_num[Rn]; setflags = (S == '1')

        def aarch32_ADC_i_T1_A_exec():
            # execute
            if self.ConditionPassed(cond):
                (result, nzcv) = self.AddWithCarry(self.R[n], imm32, self.APSR.C);
                if d == 15:          # Can only occur for A32 encoding
                    if setflags:
                        raise Exception(f'ALUExceptionReturn({result})')
                    else:
                        pass #self.ALUWritePC(result);
                else:
                    self.R[d] = result
                    if setflags:
                        self.APSR.update(nzcv)
        return aarch32_ADC_i_T1_A_exec

    #def ADC(self, setflags=False, cond=None, d=None, n=None, dn=None, m=None, imm32=None, shift_t=None, shift_n=None):
    #    if d is None and n is None:
    #        d = dn
    #        n = dn
    #    if self.ConditionPassed(cond):
    #        if imm32 is not None:
    #            (result,carry,overflow ) = self.AddWithCarry(self.R[n],imm32,self.APSR.C)
    #        else:
    #            shifted = self.Shift(self.R[m],shift_t,shift_n,self.APSR.C)
    #            (result,carry,overflow ) = self.AddWithCarry(self.R[n],shifted,self.APSR.C)
    #        self.R[d] = result
    #        if setflags:
    #            self.APSR.N=(result>>31)!=0
    #            self.APSR.Z= (result == 0)
    #            self.APSR.C= carry
    #            self.APSR.V= overflow

if __name__ == '__main__':
    c = Core(0, 0x20001000)
    step1 = c.getExec('adc', 'r0, #10', 0)
    step2 = c.getExec('adcs', 'r1, r0, #-10', 0)
    step3 = c.getExec('adcs', 'r1, #1', 0)

    step1()
    c.showRegisters()
    step2()
    c.showRegisters()
    step3()
    c.showRegisters()