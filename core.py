
class ProgramStatus:
    def __init__(self):
        self.N = False
        self.Z = False
        self.C = False
        self.V = False
        self.Q = False
        self.GE = [False] * 4

class Core:
    def __init__(self, pc, sp):
        self.R = {i:0 for i range(13)}
        self.PC = pc
        self.SP = sp
        self.LR = 0xffffffff

    def ConditionPassed(self, cond):
        return True

    def AddWithCarry(self, src1, src2, carry):
        result = src1 + src2 + carry
        return (result & 0xffffffff, (result & 0x100000000 != 0), abs(result) > 2**31)

    def Shift(self, src1, shift_t, shift_n, carry):
        result = src1 & 0xffffffff
        if shift_t == 'RRX':
            next_carry = (result & 1) != 0
            result = (result >> 1) + carry * 0x80000000
        elif shift_t == 'ROR':
            next_carry = (result & 1) != 0
            result = (result >> 1) + carry * 0x80000000

    def Shift_C(self, value, shift_t, shift_n, carry)
        if shift_n == 0:
            (result, carry_out) = (value, carry_in)
        else:
            if shift_t == 'LSL':
                (result, carry_out) = self.LSL_C(value, shift_n);
            elif shift_t == 'LSR':
                (result, carry_out) = self.LSR_C(value, shift_n);
            elif shift_t == 'ASR':
                (result, carry_out) = self.ASR_C(value, shift_n);
            elif shift_t == 'ROR':
18 (result, carry_out) = ROR_C(value, amount);
19 when SRType_RRX
20 (result, carry_out) = RRX_C(value, carry_in);
21
22 return (result, carry_out)

    def ADC(self, setflags=False, cond=None, d=None, n=None, dn=None, m=None, imm32=None, shift_t=None, shift_n=None):
        if d is None and n is None:
            d = dn
            n = dn
        if self.ConditionPassed(cond):
            if imm32 is not None:
                (result,carry,overflow ) = self.AddWithCarry(self.R[n],imm32,self.APSR.C)
            else:
                shifted = self.Shift(self.R[m],shift_t,shift_n,self.APSR.C)
                (result,carry,overflow ) = self.AddWithCarry(self.R[n],shifted,self.APSR.C)
            self.R[d] = result
            if setflags:
                self.APSR.N=(result>>31)!=0
                self.APSR.Z= (result == 0)
                self.APSR.C= carry
                self.APSR.V= overflow
