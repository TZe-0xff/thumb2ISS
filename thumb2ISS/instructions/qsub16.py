import re, logging

log = logging.getLogger('Mnem.QSUB16')
# instruction aarch32_QSUB16_A
# pattern QSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),15,0));
            diff2 = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignedSat(diff1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignedSat(diff2, 16)));
        else:
            log.debug(f'aarch32_QSUB16_T1_A_exec skipped')
    return aarch32_QSUB16_T1_A_exec


patterns = {
    'QSUB16': [
        (re.compile(r'^QSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QSUB16_T1_A, {}),
    ],
}
