#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.CLREX')
# instruction aarch32_CLREX_A
# pattern CLREX{<c>}{<q>} with bitdiffs=[]
# regex ^CLREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$ : c
def aarch32_CLREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_CLREX_T1_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_CLREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.ClearExclusiveLocal(core.ProcessorID());
        else:
            log.debug(f'aarch32_CLREX_T1_A_exec skipped')
    return aarch32_CLREX_T1_A_exec


patterns = {
    'CLREX': [
        (re.compile(r'^CLREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$', re.I), aarch32_CLREX_T1_A, {}),
    ],
}
