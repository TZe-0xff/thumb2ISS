#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.STREXB')
# instruction aarch32_STREXB_A
# pattern STREXB{<c>}{<q>} <Rd>, <Rt>, [<Rn>] with bitdiffs=[]
# regex ^STREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rd Rt Rn
def aarch32_STREXB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_STREXB_T1_A Rd={Rd} Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if d == 15 or t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == n or d == t:
        raise Exception('UNPREDICTABLE');

    def aarch32_STREXB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            if core.ExclusiveMonitorsPass(address,1):
                core.WriteMemA(address,1, core.Field(core.readR(t),7,0));
                core.writeR(d, core.ZeroExtend('0', 32));
            else:
                core.writeR(d, core.ZeroExtend('1', 32));
        else:
            log.debug(f'aarch32_STREXB_T1_A_exec skipped')
    return aarch32_STREXB_T1_A_exec


patterns = {
    'STREXB': [
        (re.compile(r'^STREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_STREXB_T1_A, {}),
    ],
}
