import re, logging

log = logging.getLogger('Mnem.UASX')
# instruction aarch32_UASX_A
# pattern UASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),31,16));
            sum  = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),15,0));
            core.R[d] = core.SetField(core.readR(d),15,0,core.Field(diff,15,0));
            core.R[d] = core.SetField(core.readR(d),31,16,core.Field(sum,15,0));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum  >= 0x10000 else '00');
        else:
            log.debug(f'aarch32_UASX_T1_A_exec skipped')
    return aarch32_UASX_T1_A_exec


patterns = {
    'UASX': [
        (re.compile(r'^UASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UASX_T1_A, {}),
    ],
}
