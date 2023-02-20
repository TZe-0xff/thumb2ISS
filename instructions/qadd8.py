import re, logging

log = logging.getLogger('Mnem.QADD8')
# instruction aarch32_QADD8_A
# pattern QADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.R[n],7,0)) + core.SInt(core.Field(core.R[m],7,0));
            sum2 = core.SInt(core.Field(core.R[n],15,8)) + core.SInt(core.Field(core.R[m],15,8));
            sum3 = core.SInt(core.Field(core.R[n],23,16)) + core.SInt(core.Field(core.R[m],23,16));
            sum4 = core.SInt(core.Field(core.R[n],31,24)) + core.SInt(core.Field(core.R[m],31,24));
            core.R[d] = core.SetField(core.R[d],7,0,core.SignedSat(sum1, 8));
            core.R[d] = core.SetField(core.R[d],15,8,core.SignedSat(sum2, 8));
            core.R[d] = core.SetField(core.R[d],23,16,core.SignedSat(sum3, 8));
            core.R[d] = core.SetField(core.R[d],31,24,core.SignedSat(sum4, 8));
        else:
            log.debug(f'aarch32_QADD8_T1_A_exec skipped')
    return aarch32_QADD8_T1_A_exec


patterns = {
    'QADD8': [
        (re.compile(r'^QADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QADD8_T1_A, {}),
    ],
}
