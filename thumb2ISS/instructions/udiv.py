import re, logging

log = logging.getLogger('Mnem.UDIV')
# instruction aarch32_UDIV_A
# pattern UDIV{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UDIV_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UDIV_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = 15;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == 15 or n == 15 or m == 15 or a != 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_UDIV_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            if core.UInt(core.R[m]) == 0:
                result = 0;
            else:
                result = core.RoundTowardsZero(core.Real(core.UInt(core.readR(n))) / core.Real(core.UInt(core.readR(m))));
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_UDIV_T1_A_exec skipped')
    return aarch32_UDIV_T1_A_exec


patterns = {
    'UDIV': [
        (re.compile(r'^UDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UDIV_T1_A, {}),
    ],
}
