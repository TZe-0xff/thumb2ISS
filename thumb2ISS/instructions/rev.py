#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.REV')
# instruction aarch32_REV_A
# pattern REV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];

    def aarch32_REV_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),7,0));
            result = core.SetField(result,23,16,core.Field(core.readR(m),15,8));
            result = core.SetField(result,15,8,core.Field(core.readR(m),23,16));
            result = core.SetField(result,7,0,core.Field(core.readR(m),31,24));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV_T1_A_exec skipped')
    return aarch32_REV_T1_A_exec

# pattern REV{<c>}.W <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern REV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV_T2_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_REV_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),7,0));
            result = core.SetField(result,23,16,core.Field(core.readR(m),15,8));
            result = core.SetField(result,15,8,core.Field(core.readR(m),23,16));
            result = core.SetField(result,7,0,core.Field(core.readR(m),31,24));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV_T2_A_exec skipped')
    return aarch32_REV_T2_A_exec


patterns = {
    'REV': [
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T1_A, {}),
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T2_A, {}),
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T2_A, {}),
    ],
}
