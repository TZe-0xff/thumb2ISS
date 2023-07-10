#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.NOP')
# instruction aarch32_NOP_A
# pattern NOP{<c>}{<q>} with bitdiffs=[]
# regex ^NOP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$ : c
def aarch32_NOP_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_NOP_T1_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_NOP_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            pass # Do nothing
        else:
            log.debug(f'aarch32_NOP_T1_A_exec skipped')
    return aarch32_NOP_T1_A_exec

# pattern NOP{<c>}.W with bitdiffs=[]
# regex ^NOP(?P<c>[ACEGHLMNPV][CEILQST])?.W$ : c
def aarch32_NOP_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_NOP_T2_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_NOP_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            pass # Do nothing
        else:
            log.debug(f'aarch32_NOP_T2_A_exec skipped')
    return aarch32_NOP_T2_A_exec


patterns = {
    'NOP': [
        (re.compile(r'^NOP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$', re.I), aarch32_NOP_T1_A, {}),
        (re.compile(r'^NOP(?P<c>[ACEGHLMNPV][CEILQST])?.W$', re.I), aarch32_NOP_T2_A, {}),
    ],
}
