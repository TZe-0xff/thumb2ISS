#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.B')
# instruction aarch32_B_A
# pattern B<c>{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T1_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T1_A_exec skipped')
    return aarch32_B_T1_A_exec

# pattern B{<c>}{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T2_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T2_A_exec skipped')
    return aarch32_B_T2_A_exec

# pattern B<c>.W <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
# pattern B<c>{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T3_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T3_A_exec skipped')
    return aarch32_B_T3_A_exec

# pattern B{<c>}.W <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
# pattern B{<c>}{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T4_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T4_A_exec skipped')
    return aarch32_B_T4_A_exec


patterns = {
    'B': [
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T1_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T2_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T3_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T3_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T4_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T4_A, {}),
    ],
}
