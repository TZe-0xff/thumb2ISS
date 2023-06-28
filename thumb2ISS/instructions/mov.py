import re, logging

log = logging.getLogger('Mnem.MOV')
# instruction aarch32_MOV_i_A
# pattern MOV<c>{<q>} <Rd>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVS{<q>} <Rd>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : Rd imm32
def aarch32_MOV_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  carry = core.APSR.C;

    def aarch32_MOV_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T1_A_exec skipped')
    return aarch32_MOV_i_T1_A_exec

# pattern MOV<c>.W <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOV{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVS.W <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : Rd imm32
# pattern MOVS{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MOV_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_i_T2_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T2_A_exec skipped')
    return aarch32_MOV_i_T2_A_exec

# pattern MOV{<c>}{<q>} <Rd>, #<imm16> with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVW{<c>}{<q>} <Rd>, #<imm16> with bitdiffs=[]
# regex ^MOVW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MOV_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_MOV_i_T3_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T3_A_exec skipped')
    return aarch32_MOV_i_T3_A_exec


# instruction aarch32_MOV_r_A
# pattern MOV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_MOV_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_MOV_r_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_MOV_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T1_A_exec skipped')
    return aarch32_MOV_r_T1_A_exec

# pattern MOV<c>{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOVS{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : Rd Rm shift_t* shift_n*
# alias   ASRS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   ASR<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSLS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSL<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSRS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSR<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
def aarch32_MOV_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MOV_r_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');

    def aarch32_MOV_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T2_A_exec skipped')
    return aarch32_MOV_r_T2_A_exec

# pattern MOV{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MOV{<c>}.W <Rd>, <Rm> {, LSL #0} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\sLSL\s#0)?$ : c Rd Rm
# pattern MOV<c>.W <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOV{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOVS{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MOVS.W <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : Rd Rm shift_t* shift_n*
# pattern MOVS{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# alias   ASRS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   ASRS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ASR<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ASR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSLS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSLS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSL<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSL{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSRS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSRS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSR<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   RORS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ROR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   RRXS{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>RRX)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : shift_t c Rd* Rm
# alias   RRX{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>RRX)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : shift_t c Rd* Rm
def aarch32_MOV_r_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MOV_r_T3_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T3_A_exec skipped')
    return aarch32_MOV_r_T3_A_exec


# instruction aarch32_MOV_rr_A
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# alias   ASRS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   ASR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   LSLS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   LSL<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   LSRS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   LSR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   RORS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   ROR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
def aarch32_MOV_rr_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    op = bitdiffs.get('op', '0')
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_rr_T1_A Rdm={Rdm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  m = core.reg_num[Rdm];  s = core.reg_num[Rs];
    setflags = (S == '1');  

    def aarch32_MOV_rr_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.readR(s),7,0));
            (result, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T1_A_exec skipped')
    return aarch32_MOV_rr_T1_A_exec

# pattern MOVS.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : Rd Rm shift_t Rs
# pattern MOVS{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV<c>.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# alias   ASRS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   ASRS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ASR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ASR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSLS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   LSLS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSL<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSL{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSRS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   LSRS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   RORS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   RORS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ROR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ROR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
def aarch32_MOV_rr_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    cond = regex_groups.get('c', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_rr_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  s = core.reg_num[Rs];
    setflags = (S == '1');  
    if d == 15 or m == 15 or s == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_rr_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.readR(s),7,0));
            (result, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T2_A_exec skipped')
    return aarch32_MOV_rr_T2_A_exec


patterns = {
    'MOV': [
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T3_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T1_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\sLSL\s#0)?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'MOVS': [
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {'S': '1'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
    'MOVW': [
        (re.compile(r'^MOVW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T3_A, {}),
    ],
    'ASRS': [
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
    'ASR': [
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'LSLS': [
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
    'LSL': [
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'LSRS': [
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
    'LSR': [
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'RORS': [
        (re.compile(r'^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
    'ROR': [
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'RRXS': [
        (re.compile(r'^(?P<shift_t>RRX)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'RRX': [
        (re.compile(r'^(?P<shift_t>RRX)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
}
