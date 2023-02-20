import re, logging

log = logging.getLogger('Mnem.QSUB')
# instruction aarch32_QSUB_A
# pattern QSUB{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QSUB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSUB_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSUB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sat = False;
            (core.R[d], sat) = core.SignedSatQ(core.SInt(core.R[m]) - core.SInt(core.R[n]), 32);
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QSUB_T1_A_exec skipped')
    return aarch32_QSUB_T1_A_exec


patterns = {
    'QSUB': [
        (re.compile(r'^QSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QSUB_T1_A, {}),
    ],
}
