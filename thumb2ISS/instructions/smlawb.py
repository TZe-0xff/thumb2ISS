import re, logging

log = logging.getLogger('Mnem.SMLAWB')
# instruction aarch32_SMLAWB_A
# pattern SMLAWB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '0')]
# regex ^SMLAWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLAWT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '1')]
# regex ^SMLAWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLAWB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLAWB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLAWB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(core.readR(n)) * core.SInt(operand2) + (core.SInt(core.readR(a)) << 16);
            core.R[d] = core.Field(result,47,16);
            if (result >> 16) != core.SInt(core.readR(d)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLAWB_T1_A_exec skipped')
    return aarch32_SMLAWB_T1_A_exec


patterns = {
    'SMLAWB': [
        (re.compile(r'^SMLAWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAWB_T1_A, {'M': '0'}),
    ],
    'SMLAWT': [
        (re.compile(r'^SMLAWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAWB_T1_A, {'M': '1'}),
    ],
}
