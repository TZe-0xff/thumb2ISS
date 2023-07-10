#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.LDREX')
# instruction aarch32_LDREX_A
# pattern LDREX{<c>}{<q>} <Rt>, [<Rn> {, #<imm>}] with bitdiffs=[]
# regex ^LDREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDREX_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) + imm32;
            core.SetExclusiveMonitors(address,4);
            core.writeR(t, core.ReadMemA(address,4));
        else:
            log.debug(f'aarch32_LDREX_T1_A_exec skipped')
    return aarch32_LDREX_T1_A_exec


patterns = {
    'LDREX': [
        (re.compile(r'^LDREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$', re.I), aarch32_LDREX_T1_A, {}),
    ],
}
