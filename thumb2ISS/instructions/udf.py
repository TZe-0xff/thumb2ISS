#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.UDF')
# instruction aarch32_UDF_A
# pattern UDF{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_UDF_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_UDF_T1_A imm32={imm32} cond={cond}')
    # decode
    # imm32 is for assembly and disassembly only, and is ignored by hardware.

    def aarch32_UDF_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            raise Exception('UNDEFINED');
        else:
            log.debug(f'aarch32_UDF_T1_A_exec skipped')
    return aarch32_UDF_T1_A_exec

# pattern UDF{<c>}.W {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?.W\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
# pattern UDF{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_UDF_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_UDF_T2_A imm32={imm32} cond={cond}')
    # decode
    # imm32 is for assembly and disassembly only, and is ignored by hardware.

    def aarch32_UDF_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            raise Exception('UNDEFINED');
        else:
            log.debug(f'aarch32_UDF_T2_A_exec skipped')
    return aarch32_UDF_T2_A_exec


patterns = {
    'UDF': [
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T1_A, {}),
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?.W\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T2_A, {}),
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T2_A, {}),
    ],
}
