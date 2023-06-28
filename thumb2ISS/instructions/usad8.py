import re, logging

log = logging.getLogger('Mnem.USAD8')
# instruction aarch32_USAD8_A
# pattern USAD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^USAD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_USAD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_USAD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            absdiff1 = core.Abs(core.UInt(core.Field(core.readR(n),7,0))   - core.UInt(core.Field(core.readR(m),7,0)));
            absdiff2 = core.Abs(core.UInt(core.Field(core.readR(n),15,8))  - core.UInt(core.Field(core.readR(m),15,8)));
            absdiff3 = core.Abs(core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16)));
            absdiff4 = core.Abs(core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24)));
            result = absdiff1 + absdiff2 + absdiff3 + absdiff4;
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_USAD8_T1_A_exec skipped')
    return aarch32_USAD8_T1_A_exec


patterns = {
    'USAD8': [
        (re.compile(r'^USAD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_USAD8_T1_A, {}),
    ],
}
