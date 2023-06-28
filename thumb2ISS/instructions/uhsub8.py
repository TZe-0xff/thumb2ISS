import re, logging

log = logging.getLogger('Mnem.UHSUB8')
# instruction aarch32_UHSUB8_A
# pattern UHSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),7,0)) - core.UInt(core.Field(core.readR(m),7,0));
            diff2 = core.UInt(core.Field(core.readR(n),15,8)) - core.UInt(core.Field(core.readR(m),15,8));
            diff3 = core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16));
            diff4 = core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(diff1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(diff2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(diff3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(diff4,8,1)));
        else:
            log.debug(f'aarch32_UHSUB8_T1_A_exec skipped')
    return aarch32_UHSUB8_T1_A_exec


patterns = {
    'UHSUB8': [
        (re.compile(r'^UHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHSUB8_T1_A, {}),
    ],
}
