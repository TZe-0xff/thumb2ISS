import re, logging

log = logging.getLogger('Mnem.USAT16')
# instruction aarch32_USAT16_A
# pattern USAT16{<c>}{<q>} <Rd>, #<imm>, <Rn> with bitdiffs=[]
# regex ^USAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$ : c Rd imm32 Rn
def aarch32_USAT16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_USAT16_T1_A Rd={Rd} imm32={imm32} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAT16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result1, sat1) = core.UnsignedSatQ(core.SInt(core.Field(core.readR(n),15,0)), imm32);
            (result2, sat2) = core.UnsignedSatQ(core.SInt(core.Field(core.readR(n),31,16)), imm32);
            core.R[d] = core.SetField(core.readR(d),15,0,core.ZeroExtend(result1, 16));
            core.R[d] = core.SetField(core.readR(d),31,16,core.ZeroExtend(result2, 16));
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_USAT16_T1_A_exec skipped')
    return aarch32_USAT16_T1_A_exec


patterns = {
    'USAT16': [
        (re.compile(r'^USAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$', re.I), aarch32_USAT16_T1_A, {}),
    ],
}