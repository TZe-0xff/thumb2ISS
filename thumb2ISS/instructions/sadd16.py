#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SADD16')
# instruction aarch32_SADD16_A
# pattern SADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),15,0));
            sum2 = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum1,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum2,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if sum1 >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum2 >= 0 else '00');
        else:
            log.debug(f'aarch32_SADD16_T1_A_exec skipped')
    return aarch32_SADD16_T1_A_exec


patterns = {
    'SADD16': [
        (re.compile(r'^SADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SADD16_T1_A, {}),
    ],
}
