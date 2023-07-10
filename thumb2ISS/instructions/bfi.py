#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.BFI')
# instruction aarch32_BFI_A
# pattern BFI{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_BFI_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_BFI_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  msbit = core.UInt(width) - 1 + core.UInt(lsb);  lsbit = core.UInt(lsb);
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit < lsbit:
        raise Exception('UNPREDICTABLE');

    def aarch32_BFI_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            mask = 0xffffffff >> (31 - msbit + lsbit);
            tmp_Rd = core.readR(d) & ~((mask) << lsbit);
            core.writeR(d, tmp_Rd | ((core.UInt(core.readR(n)) & mask) << lsbit));
            # Other bits of core.readR(d) are unchanged
        else:
            log.debug(f'aarch32_BFI_T1_A_exec skipped')
    return aarch32_BFI_T1_A_exec


patterns = {
    'BFI': [
        (re.compile(r'^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_BFI_T1_A, {}),
    ],
}
