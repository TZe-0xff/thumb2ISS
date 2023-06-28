import re, logging

log = logging.getLogger('Mnem.SMULBB')
# instruction aarch32_SMULBB_A
# pattern SMULBB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMULBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULBT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMULBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULTB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMULTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULTT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMULTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMULBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMULBB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    n_high = (N == '1');  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMULBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.readR(n),31,16) if n_high else core.Field(core.readR(n),15,0);
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(operand1) * core.SInt(operand2);
            core.writeR(d, core.Field(result,31,0));
            # Signed overflow cannot occur
        else:
            log.debug(f'aarch32_SMULBB_T1_A_exec skipped')
    return aarch32_SMULBB_T1_A_exec


patterns = {
    'SMULBB': [
        (re.compile(r'^SMULBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMULBT': [
        (re.compile(r'^SMULBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMULTB': [
        (re.compile(r'^SMULTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMULTT': [
        (re.compile(r'^SMULTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '1', 'M': '1'}),
    ],
}
