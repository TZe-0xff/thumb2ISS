import struct
import re
import binascii

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
    

    def update(self, flags):
        print(flags)
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
        self.reg_num.update({'SP':13, 'sp':13, 'LR':14, 'lr':14, 'PC':15, 'pc':15})
        self.APSR = ProgramStatus()
        self.bytes_to_Uint = ['', '<B', '<H', '', '<L']
        

        self.instructions = {
            'ADC' : [
                (re.compile(r'^ADC(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)$', re.I), self.aarch32_ADC_i_T1_A, {'S':'0'}),
                ],
            'ADCS' : [
                (re.compile(r'^ADCS(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)$', re.I), self.aarch32_ADC_i_T1_A, {'S':'1'}),
                ],
            'LDR' : [
                (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC, #(?P<imm32>[+-]?\d+)\]$', re.I), self.aarch32_LDR_l_T2_A, {}),
                (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), self.aarch32_LDR_i_T1_A, {}),
                (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), self.aarch32_LDR_i_T4_A, {'P':'1','U':'0','W':'0'}),
                (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), self.aarch32_LDR_i_T4_A, {'P':'0','W':'1'}),
                (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), self.aarch32_LDR_i_T4_A, {'P':'1','W':'1'}),
            ]
        }

    @property
    def PC(self):
        return self.R[15] + 4

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

    def showRegisters(self):
        for i in range(13):
            print(f'r{i}: {hex(self.UInt(self.R[i]))}', end='  ')
            if i%4 == 3:
                print('')
        print(f'sp: {hex(self.UInt(self.R[13]))}', end='  ')
        print(f'lr: {hex(self.UInt(self.R[14]))}', end='  ')
        print(f'pc: {hex(self.UInt(self.R[15]))}')
        print(self.APSR)

    def getExec(self, mnem, args, expected_pc):
        m = None
        for pat, action, bitdiffs in self.instructions.get(mnem.upper(), []):
            m = pat.match(f'{mnem} {args}')
            if m is not None:
                break
        if m is not None:
            instr_exec = action(m, bitdiffs)
            def mnem_exec():
                assert(expected_pc == self.UInt(self.R[15]))
                instr_exec()
            return mnem_exec
        def debug_exec():
            print(f'Unsupported {mnem} execution')
        return debug_exec


    
    def Field(self, value, msb=31, lsb=0):
        mask = (0xffffffff >> (31 - msb + lsb)) << lsb
        val = (value & mask) >> lsb
        return Register(struct.pack('<L', val))

    def UInt(self, value):
        if type(value) == Register:
            value = value.bval
        elif type(value) == str or type(value) == int:
            value = struct.pack('<l', int(value, 0))
        if type(value) == bytes:
            return struct.unpack('<L', value)[0]
        return int(value)
        

    def SInt(self, value):
        if type(value) == Register:
            return value.ival
        elif type(value) == str or type(value) == int:
            value = struct.pack('<l', int(value, 0))
        if type(value) == bytes:
            return struct.unpack('<l', value)[0]
        return int(value)

    def Bit(self, value, bit_pos=31):
        if type(value) == bytes:
            return (self.UInt(value) & (1 << bit_pos)) != 0
        return (value & (1 << bit_pos)) != 0

    def IsZero(self, value):
        if type(value) == Register:
            return (value.ival == 0)
        elif type(value) == bytes:
            return (self.UInt(value) == 0)
        return (int(value) == 0)


    def ConditionPassed(self, cond):
        return True

    def ReadMemU(self, address, size):
        assert(size in [1,2,4])
        print(f'Read {size} bytes from {hex(address.ival)}')
        byte_seq = b''.join(self.memory[i] for i in range(address.ival, address.ival + size))
        # load as unsigned
        value = struct.unpack(self.bytes_to_Uint[size], byte_seq)[0]
        return Register(struct.pack('<L', value))

    def Align(self, reg_value, boundary):
        address = self.UInt(reg_value) & ~(boundary-1)
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
        print(self.UInt(x), self.UInt(y))
        signed_sum = self.SInt(x) + self.SInt(y) + self.UInt(carry_in);
        result = self.Field(unsigned_sum, 31, 0) # same value as signed_sum<N-1:0>
        nzcv = {'N': self.Bit(result, 31),
                'Z' : self.IsZero(result),
                'C' : self.UInt(result) != unsigned_sum,
                'V' : self.SInt(result) != signed_sum
                }
        carry_out = nzcv['C']
        print(f'Carry is {carry_out} because result {binascii.hexlify(result.bval)} vs {unsigned_sum}')
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

    #pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=
    #LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:, #(?P<imm32>[+]?\d+))?\]
    def aarch32_LDR_i_T1_A(self, regex_match, bitdiffs):
        # decode 
        Rt = regex_match.group('Rt')
        Rn = regex_match.group('Rn')
        cond = regex_match.group('c')
        imm32 = regex_match.group('imm32')
        if imm32 is None:
            imm32 = '0'
        print(f'aarch32_LDR_i_T1_A {Rt}, [{Rn}, #{imm32}]')
        t = self.reg_num[Rt]; n = self.reg_num[Rn]
        index = True; add = True; wback = False;

        def aarch32_LDR_i_T1_A_exec():
            # execute
            offset_addr = (self.R[n] + imm32) if add else (self.R[n] - imm32);
            address = offset_addr if index else self.R[n];
            data = self.ReadMemU(address,4);
            if wback : self.R[n] = offset_addr;
            if t == 15 :
                if self.Field(address,1,0) == 0:
                    pass #self.LoadWritePC(data);
                else:
                    raise Exception('UNPREDICTABLE');
            else:
                self.R[t] = data;

        return aarch32_LDR_i_T1_A_exec


    #pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=P == 1 && U == 0 && W == 0
    #LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:, #-(?P<imm32>\d+))?\]
    #pattern LDR{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=P == 0 && W == 1
    #LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)
    #pattern LDR{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=P == 1 && W == 1
    #LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!
    def aarch32_LDR_i_T4_A(self, regex_match, bitdiffs):
        # decode 
        Rt = regex_match.group('Rt')
        Rn = regex_match.group('Rn')
        cond = regex_match.group('c')
        imm32 = regex_match.group('imm32')
        P = bitdiffs.get('P', '0')
        W = bitdiffs.get('W', '0')
        U = bitdiffs.get('U', '1')
        if imm32 is None:
            imm32 = '0'
        print(f'aarch32_LDR_i_T4_A {Rt}, [{Rn}, #{imm32}] ({bitdiffs})')
        t = self.reg_num[Rt]; n = self.reg_num[Rn]
        index = (P == '1'); add = (U == '1'); wback = (W == '1');

        def aarch32_LDR_i_T4_A_exec():
            # execute
            offset_addr = (self.R[n] + imm32) if add else (self.R[n] - imm32);
            address = offset_addr if index else self.R[n];
            data = self.ReadMemU(address,4);
            if wback : self.R[n] = offset_addr;
            if t == 15 :
                if self.Field(address,1,0) == 0:
                    pass #self.LoadWritePC(data);
                else:
                    raise Exception('UNPREDICTABLE');
            else:
                self.R[t] = data;

        return aarch32_LDR_i_T4_A_exec


    #pattern LDR{<c>}.W <Rt>, <label> with bitdiffs=[]
    #pattern LDR{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
    #pattern LDR{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
    #LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC, #(?P<imm32>[+-]?\d+))?\]
    def aarch32_LDR_l_T2_A(self, regex_match, bitdiffs):
        # decode
        Rt = regex_match.group('Rt')
        cond = regex_match.group('c')
        imm32 = regex_match.group('imm32')
        U = bitdiffs.get('U', '1')
        
        t = self.reg_num[Rt];  add = (U == '1');

        def aarch32_LDR_l_T2_A_exec():
            # execute
            base = self.Align(self.PC,4);
            address = (base + imm32) if add else (base - imm32);
            data = self.ReadMemU(address,4);
            if t == 15 :
                if self.Field(address,1,0) == 0:
                    pass #self.LoadWritePC(data);
                else:
                    raise Exception('UNPREDICTABLE');
            else:
                self.R[t] = data;

        return aarch32_LDR_l_T2_A_exec
        

if __name__ == '__main__':
    initial_mem = {i:struct.pack('B',i) for i in range(256)}
    c = Core()
    c.configure(0, 0x20001000, initial_mem)
    steps = []
    steps += [c.getExec('adc', 'r0, #10', 0)]
    steps += [c.getExec('adcs', 'r1, r0, #-10', 0)]
    steps += [c.getExec('adcs', 'r1, #1', 0)]
    steps += [c.getExec('ldr', 'r5, [pc, #28]', 0)]
    steps += [c.getExec('ldr', 'r4, [r4]', 0)]
    steps += [c.getExec('ldr', 'r3, [r1, #-1]', 0)]
    steps += [c.getExec('ldr', 'r3, [r1, #-1]!', 0)]
    steps += [c.getExec('ldr', 'r2, [r1], #+3', 0)]

    for s in steps:
        print(s)
        s()
        c.showRegisters()
        print('-'*20)