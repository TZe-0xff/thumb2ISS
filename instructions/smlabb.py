import re, logging

log = logging.getLogger('Mnem.SMLABB')
# instruction aarch32_SMLABB_A
# pattern SMLABB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMLABB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLABT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMLABT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLATB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMLATB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLATT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMLATT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLABB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLABB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    n_high = (N == '1');  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLABB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.R[n],31,16) if n_high else core.Field(core.R[n],15,0);
            operand2 = core.Field(core.R[m],31,16) if m_high else core.Field(core.R[m],15,0);
            result = core.SInt(operand1) * core.SInt(operand2) + core.SInt(core.R[a]);
            core.R[d] = core.Field(result,31,0);
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLABB_T1_A_exec skipped')
    return aarch32_SMLABB_T1_A_exec


patterns = {
    'SMLABB': [
        (re.compile(r'^SMLABB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMLABT': [
        (re.compile(r'^SMLABT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMLATB': [
        (re.compile(r'^SMLATB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMLATT': [
        (re.compile(r'^SMLATT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '1', 'M': '1'}),
    ],
}
