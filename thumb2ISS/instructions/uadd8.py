#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.UADD8')
# instruction aarch32_UADD8_A
# pattern UADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m  == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),7,0)) + core.UInt(core.Field(core.readR(m),7,0));
            sum2 = core.UInt(core.Field(core.readR(n),15,8)) + core.UInt(core.Field(core.readR(m),15,8));
            sum3 = core.UInt(core.Field(core.readR(n),23,16)) + core.UInt(core.Field(core.readR(m),23,16));
            sum4 = core.UInt(core.Field(core.readR(n),31,24)) + core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,7,0)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,7,0)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,7,0)));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if sum1 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if sum2 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if sum3 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if sum4 >= 0x100 else '0')
        else:
            log.debug(f'aarch32_UADD8_T1_A_exec skipped')
    return aarch32_UADD8_T1_A_exec


patterns = {
    'UADD8': [
        (re.compile(r'^UADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UADD8_T1_A, {}),
    ],
}
