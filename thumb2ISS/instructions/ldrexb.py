#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.LDREXB')
# instruction aarch32_LDREXB_A
# pattern LDREXB{<c>}{<q>} <Rt>, [<Rn>] with bitdiffs=[]
# regex ^LDREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rt Rn
def aarch32_LDREXB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_LDREXB_T1_A Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREXB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            core.SetExclusiveMonitors(address,1);
            core.writeR(t, core.ZeroExtend(core.ReadMemA(address,1), 32));
        else:
            log.debug(f'aarch32_LDREXB_T1_A_exec skipped')
    return aarch32_LDREXB_T1_A_exec


patterns = {
    'LDREXB': [
        (re.compile(r'^LDREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_LDREXB_T1_A, {}),
    ],
}
