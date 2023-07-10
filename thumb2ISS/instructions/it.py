#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.IT')
# instruction aarch32_IT_A
# pattern IT{<x>{<y>{<z>}}}{<q>} <cond> with bitdiffs=[]
# regex ^IT(?P<mask>[ET]*)(?:\.[NW])?\s(?P<firstcond>\w\w)$ : mask firstcond
def aarch32_IT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    mask = regex_groups.get('mask', None)
    firstcond = regex_groups.get('firstcond', None)
    log.debug(f'aarch32_IT_T1_A mask={mask} firstcond={firstcond}')
    # decode

    def aarch32_IT_T1_A_exec():
        # execute
        core.CheckITEnabled(mask);
        core.APSR.ITcond = firstcond; core.APSR.ITsteps = len(mask)
        ShouldAdvanceIT = False;
    return aarch32_IT_T1_A_exec


patterns = {
    'IT': [
        (re.compile(r'^IT(?P<mask>[ET]*)(?:\.[NW])?\s(?P<firstcond>\w\w)$', re.I), aarch32_IT_T1_A, {}),
    ],
}
