import re, logging

log = logging.getLogger('Mnem.SASX')
# instruction aarch32_SASX_A
# pattern SASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.SInt(core.Field(core.R[n],15,0)) - core.SInt(core.Field(core.R[m],31,16));
            sum  = core.SInt(core.Field(core.R[n],31,16)) + core.SInt(core.Field(core.R[m],15,0));
            core.R[d] = core.SetField(core.R[d],15,0,core.Field(diff,15,0));
            core.R[d] = core.SetField(core.R[d],31,16,core.Field(sum,15,0));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum  >= 0 else '00');
        else:
            log.debug(f'aarch32_SASX_T1_A_exec skipped')
    return aarch32_SASX_T1_A_exec


patterns = {
    'SASX': [
        (re.compile(r'^SASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SASX_T1_A, {}),
    ],
}