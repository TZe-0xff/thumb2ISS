#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.BFC')
# instruction aarch32_BFC_A
# pattern BFC{<c>}{<q>} <Rd>, #<lsb>, #<width> with bitdiffs=[]
# regex ^BFC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd lsb width
def aarch32_BFC_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_BFC_T1_A Rd={Rd} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  msbit = core.UInt(width) - 1 + core.UInt(lsb);  lsbit = core.UInt(lsb);
    if d == 15:
        raise Exception('UNPREDICTABLE');  # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit < lsbit:
        raise Exception('UNPREDICTABLE');

    def aarch32_BFC_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.readR(d) & ~((0xffffffff >> (31 - msbit + lsbit)) << lsbit));
            # Other bits of core.readR(d) are unchanged
        else:
            log.debug(f'aarch32_BFC_T1_A_exec skipped')
    return aarch32_BFC_T1_A_exec


patterns = {
    'BFC': [
        (re.compile(r'^BFC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_BFC_T1_A, {}),
    ],
}
