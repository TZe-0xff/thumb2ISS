import re, logging

log = logging.getLogger('Mnem.CLZ')
# instruction aarch32_CLZ_A
# pattern CLZ{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^CLZ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_CLZ_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = Rm
    log.debug(f'aarch32_CLZ_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CLZ_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.CountLeadingZeroBits(core.readR(m));
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_CLZ_T1_A_exec skipped')
    return aarch32_CLZ_T1_A_exec


patterns = {
    'CLZ': [
        (re.compile(r'^CLZ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CLZ_T1_A, {}),
    ],
}
