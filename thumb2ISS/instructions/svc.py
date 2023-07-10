#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SVC')
# instruction aarch32_SVC_A
# pattern SVC{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^SVC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_SVC_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SVC_T1_A imm32={imm32} cond={cond}')
    # decode

    def aarch32_SVC_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.CheckForSVCTrap(core.Field(imm32,15,0));
            core.CallSupervisor(core.Field(imm32,15,0));
        else:
            log.debug(f'aarch32_SVC_T1_A_exec skipped')
    return aarch32_SVC_T1_A_exec


patterns = {
    'SVC': [
        (re.compile(r'^SVC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_SVC_T1_A, {}),
    ],
}
