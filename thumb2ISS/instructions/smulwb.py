#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SMULWB')
# instruction aarch32_SMULWB_A
# pattern SMULWB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMULWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULWT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMULWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMULWB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMULWB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMULWB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            product = core.SInt(core.readR(n)) * core.SInt(operand2);
            core.writeR(d, core.Field(product,47,16));
            # Signed overflow cannot occur
        else:
            log.debug(f'aarch32_SMULWB_T1_A_exec skipped')
    return aarch32_SMULWB_T1_A_exec


patterns = {
    'SMULWB': [
        (re.compile(r'^SMULWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULWB_T1_A, {'M': '0'}),
    ],
    'SMULWT': [
        (re.compile(r'^SMULWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULWB_T1_A, {'M': '1'}),
    ],
}
