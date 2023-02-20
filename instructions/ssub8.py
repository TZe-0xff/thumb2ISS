import re, logging

log = logging.getLogger('Mnem.SSUB8')
# instruction aarch32_SSUB8_A
# pattern SSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.R[n],7,0)) - core.SInt(core.Field(core.R[m],7,0));
            diff2 = core.SInt(core.Field(core.R[n],15,8)) - core.SInt(core.Field(core.R[m],15,8));
            diff3 = core.SInt(core.Field(core.R[n],23,16)) - core.SInt(core.Field(core.R[m],23,16));
            diff4 = core.SInt(core.Field(core.R[n],31,24)) - core.SInt(core.Field(core.R[m],31,24));
            core.R[d] = core.SetField(core.R[d],7,0,core.Field(diff1,7,0));
            core.R[d] = core.SetField(core.R[d],15,8,core.Field(diff2,7,0));
            core.R[d] = core.SetField(core.R[d],23,16,core.Field(diff3,7,0));
            core.R[d] = core.SetField(core.R[d],31,24,core.Field(diff4,7,0));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if diff1 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if diff2 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if diff3 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if diff4 >= 0 else '0')
        else:
            log.debug(f'aarch32_SSUB8_T1_A_exec skipped')
    return aarch32_SSUB8_T1_A_exec


patterns = {
    'SSUB8': [
        (re.compile(r'^SSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SSUB8_T1_A, {}),
    ],
}
