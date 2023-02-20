import re, logging

log = logging.getLogger('Mnem.CMN')
# instruction aarch32_CMN_i_A
# pattern CMN{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMN_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], imm32, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_i_T1_A_exec skipped')
    return aarch32_CMN_i_T1_A_exec


# instruction aarch32_CMN_r_A
# pattern CMN{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMN_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMN_r_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_CMN_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], shifted, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_r_T1_A_exec skipped')
    return aarch32_CMN_r_T1_A_exec

# pattern CMN{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern CMN{<c>}.W <Rn>, <Rm> with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
# pattern CMN{<c>}{<q>} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rn Rm shift_t* shift_n*
def aarch32_CMN_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_CMN_r_T2_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CMN_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], shifted, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_r_T2_A_exec skipped')
    return aarch32_CMN_r_T2_A_exec


patterns = {
    'CMN': [
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMN_i_T1_A, {}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMN_r_T1_A, {}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
    ],
}
