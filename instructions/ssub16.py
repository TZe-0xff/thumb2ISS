import re, logging

log = logging.getLogger('Mnem.SSUB16')
# instruction aarch32_SSUB16_A
# pattern SSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.R[n],15,0)) - core.SInt(core.Field(core.R[m],15,0));
            diff2 = core.SInt(core.Field(core.R[n],31,16)) - core.SInt(core.Field(core.R[m],31,16));
            core.R[d] = core.SetField(core.R[d],15,0,core.Field(diff1,15,0));
            core.R[d] = core.SetField(core.R[d],31,16,core.Field(diff2,15,0));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff1 >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if diff2 >= 0 else '00');
        else:
            log.debug(f'aarch32_SSUB16_T1_A_exec skipped')
    return aarch32_SSUB16_T1_A_exec


patterns = {
    'SSUB16': [
        (re.compile(r'^SSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SSUB16_T1_A, {}),
    ],
}
