#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.SMMLS')
# instruction aarch32_SMMLS_A
# pattern SMMLS{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '0')]
# regex ^SMMLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMMLSR{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '1')]
# regex ^SMMLSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMMLS_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_SMMLS_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  round = (R == '1');
    if d == 15 or n == 15 or m == 15 or a == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMLS_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.SInt(core.readR(a)) << 32) - core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            if round:
                 result = result + 0x80000000;
            core.writeR(d, core.Field(result,63,32));
        else:
            log.debug(f'aarch32_SMMLS_T1_A_exec skipped')
    return aarch32_SMMLS_T1_A_exec


patterns = {
    'SMMLS': [
        (re.compile(r'^SMMLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLS_T1_A, {'R': '0'}),
    ],
    'SMMLSR': [
        (re.compile(r'^SMMLSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLS_T1_A, {'R': '1'}),
    ],
}
