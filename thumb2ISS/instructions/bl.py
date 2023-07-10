#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.BL')
# instruction aarch32_BL_i_A
# pattern BL{<c>}{<q>} <label> with bitdiffs=[]
# regex ^BL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_BL_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_BL_i_T1_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_BL_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                targetAddress = abs_address;
            core.BranchWritePC(targetAddress, 'DIRCALL');
        else:
            log.debug(f'aarch32_BL_i_T1_A_exec skipped')
    return aarch32_BL_i_T1_A_exec

# pattern BLX{<c>}{<q>} <label> with bitdiffs=[]
# regex ^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_BL_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    H = bitdiffs.get('H', '0')
    log.debug(f'aarch32_BL_i_T2_A abs_address={hex(abs_address)} cond={cond}')
    # decode
    if H == '1':
        raise Exception('UNDEFINED');

    def aarch32_BL_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                targetAddress = abs_address;
            core.BranchWritePC(targetAddress, 'DIRCALL');
        else:
            log.debug(f'aarch32_BL_i_T2_A_exec skipped')
    return aarch32_BL_i_T2_A_exec


patterns = {
    'BL': [
        (re.compile(r'^BL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_BL_i_T1_A, {}),
    ],
    'BLX': [
        (re.compile(r'^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_BL_i_T2_A, {}),
    ],
}
