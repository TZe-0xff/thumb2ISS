import re, logging

log = logging.getLogger('Mnem.SMMUL')
# instruction aarch32_SMMUL_A
# pattern SMMUL{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('R', '0')]
# regex ^SMMUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMMULR{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('R', '1')]
# regex ^SMMULR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMMUL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    R = bitdiffs.get('R', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMMUL_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  round = (R == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMUL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            if round:
                 result = result + 0x80000000;
            core.R[d] = core.Field(result,63,32);
        else:
            log.debug(f'aarch32_SMMUL_T1_A_exec skipped')
    return aarch32_SMMUL_T1_A_exec


patterns = {
    'SMMUL': [
        (re.compile(r'^SMMUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMMUL_T1_A, {'R': '0'}),
    ],
    'SMMULR': [
        (re.compile(r'^SMMULR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMMUL_T1_A, {'R': '1'}),
    ],
}
