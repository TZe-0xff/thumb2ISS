import re, logging

log = logging.getLogger('Mnem.QDADD')
# instruction aarch32_QDADD_A
# pattern QDADD{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QDADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QDADD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QDADD_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QDADD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (doubled, sat1) = core.SignedSatQ(2 * core.SInt(core.readR(n)), 32);
            sat2 = False;
            (core.R[d], sat2)  = core.SignedSatQ(core.SInt(core.readR(m)) + core.SInt(doubled), 32);
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QDADD_T1_A_exec skipped')
    return aarch32_QDADD_T1_A_exec


patterns = {
    'QDADD': [
        (re.compile(r'^QDADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QDADD_T1_A, {}),
    ],
}
