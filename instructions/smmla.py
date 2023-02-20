import re, logging

log = logging.getLogger('Mnem.SMMLA')
# instruction aarch32_SMMLA_A
# pattern SMMLA{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '0')]
# regex ^SMMLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMMLAR{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '1')]
# regex ^SMMLAR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMMLA_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_SMMLA_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  round = (R == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMLA_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.SInt(core.R[a]) << 32) + core.SInt(core.R[n]) * core.SInt(core.R[m]);
            if round:
                 result = result + 0x80000000;
            core.R[d] = core.Field(result,63,32);
        else:
            log.debug(f'aarch32_SMMLA_T1_A_exec skipped')
    return aarch32_SMMLA_T1_A_exec


patterns = {
    'SMMLA': [
        (re.compile(r'^SMMLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLA_T1_A, {'R': '0'}),
    ],
    'SMMLAR': [
        (re.compile(r'^SMMLAR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLA_T1_A, {'R': '1'}),
    ],
}
