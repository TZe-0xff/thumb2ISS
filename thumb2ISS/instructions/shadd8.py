#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SHADD8')
# instruction aarch32_SHADD8_A
# pattern SHADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),7,0)) + core.SInt(core.Field(core.readR(m),7,0));
            sum2 = core.SInt(core.Field(core.readR(n),15,8)) + core.SInt(core.Field(core.readR(m),15,8));
            sum3 = core.SInt(core.Field(core.readR(n),23,16)) + core.SInt(core.Field(core.readR(m),23,16));
            sum4 = core.SInt(core.Field(core.readR(n),31,24)) + core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,8,1)));
        else:
            log.debug(f'aarch32_SHADD8_T1_A_exec skipped')
    return aarch32_SHADD8_T1_A_exec


patterns = {
    'SHADD8': [
        (re.compile(r'^SHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHADD8_T1_A, {}),
    ],
}
