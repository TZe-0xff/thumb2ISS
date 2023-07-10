#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SMUAD')
# instruction aarch32_SMUAD_A
# pattern SMUAD{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMUAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMUADX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMUADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMUAD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMUAD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMUAD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 + product2;
            core.writeR(d, core.Field(result,31,0));
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMUAD_T1_A_exec skipped')
    return aarch32_SMUAD_T1_A_exec


patterns = {
    'SMUAD': [
        (re.compile(r'^SMUAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUAD_T1_A, {'M': '0'}),
    ],
    'SMUADX': [
        (re.compile(r'^SMUADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUAD_T1_A, {'M': '1'}),
    ],
}
