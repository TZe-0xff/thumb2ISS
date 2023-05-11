import re, logging

log = logging.getLogger('Mnem.SEL')
# instruction aarch32_SEL_A
# pattern SEL{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SEL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SEL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SEL_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SEL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.R[d] = core.SetField(core.readR(d),7,0,core.Field(core.readR(n),7,0)   if core.APSR.GE[0] else core.Field(core.readR(m),7,0));
            core.R[d] = core.SetField(core.readR(d),15,8,core.Field(core.readR(n),15,8)  if core.APSR.GE[1] else core.Field(core.readR(m),15,8));
            core.R[d] = core.SetField(core.readR(d),23,16,core.Field(core.readR(n),23,16) if core.APSR.GE[2] else core.Field(core.readR(m),23,16));
            core.R[d] = core.SetField(core.readR(d),31,24,core.Field(core.readR(n),31,24) if core.APSR.GE[3] else core.Field(core.readR(m),31,24));
        else:
            log.debug(f'aarch32_SEL_T1_A_exec skipped')
    return aarch32_SEL_T1_A_exec


patterns = {
    'SEL': [
        (re.compile(r'^SEL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SEL_T1_A, {}),
    ],
}
