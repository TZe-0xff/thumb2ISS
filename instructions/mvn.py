import re, logging

log = logging.getLogger('Mnem.MVN')
# instruction aarch32_MVN_i_A
# pattern MVN{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MVNS{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MVN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MVN_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MVN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.NOT(imm32);
            if d == 15:
                          # Can only occur for A32 encoding
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
            log.debug(f'aarch32_MVN_i_T1_A_exec skipped')
    return aarch32_MVN_i_T1_A_exec


# instruction aarch32_MVN_r_A
# pattern MVN<c>{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern MVNS{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^MVNS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : Rd Rm
def aarch32_MVN_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_MVN_r_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = not (cond is not None);
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_MVN_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
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
            log.debug(f'aarch32_MVN_r_T1_A_exec skipped')
    return aarch32_MVN_r_T1_A_exec

# pattern MVN{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MVN<c>.W <Rd>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern MVN{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MVNS{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MVNS.W <Rd>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : Rd Rm
# pattern MVNS{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
def aarch32_MVN_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_MVN_r_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MVN_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
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
            log.debug(f'aarch32_MVN_r_T2_A_exec skipped')
    return aarch32_MVN_r_T2_A_exec


patterns = {
    'MVN': [
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MVN_i_T1_A, {'S': '0'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T1_A, {}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'MVNS': [
        (re.compile(r'^MVNS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T1_A, {}),
        (re.compile(r'^MVNS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MVN_i_T1_A, {'S': '1'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
}
