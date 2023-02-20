import re, logging

log = logging.getLogger('Mnem.MOV')
# instruction aarch32_MOV_i_A
# pattern MOV<c>{<q>} <Rd>, #<imm8> with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVS{<q>} <Rd>, #<imm8> with bitdiffs=[]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : Rd imm32
def aarch32_MOV_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_MOV_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = not (cond is not None);  carry = core.APSR.C;

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
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T1_A_exec skipped')
    return aarch32_MOV_r_T1_A_exec

# pattern MOV<c>{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOVS{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : Rd Rm shift_t* shift_n*
def aarch32_MOV_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MOV_r_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = not (cond is not None);

    def aarch32_MOV_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T3_A_exec skipped')
    return aarch32_MOV_r_T3_A_exec


patterns = {
    'MOV': [
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T3_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T1_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\sLSL\s#0)?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
    ],
    'MOVS': [
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
    ],
}
