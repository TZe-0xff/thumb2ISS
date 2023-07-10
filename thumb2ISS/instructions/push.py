#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.PUSH')
# instruction aarch32_PUSH_A
# pattern PUSH{<c>}{<q>} <registers> with bitdiffs=[]
# regex ^PUSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$ : c registers
# pattern STMDB{<c>}{<q>} SP!, <registers> with bitdiffs=[]
# regex ^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$ : c registers
def aarch32_PUSH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_PUSH_T1_A cond={cond} reg_list={reg_list}')
    # decode
    UnalignedAllowed = False;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_PUSH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(13) - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == 13 and i != core.LowestSetBit(registers):  # Only possible for encoding A1
                        core.WriteMemA(address,4, UNKNOWN = 0);
                    else:
                        if UnalignedAllowed:
                            core.WriteMemU(address,4, core.readR(i));
                        else:
                            core.WriteMemA(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1 or A2
                if UnalignedAllowed:
                    core.WriteMemU(address,4, core.PCStoreValue());
                else:
                    core.WriteMemA(address,4, core.PCStoreValue());
            core.writeR(13, core.readR(13) - 4*registers.count('1'));
        else:
            log.debug(f'aarch32_PUSH_T1_A_exec skipped')
    return aarch32_PUSH_T1_A_exec


patterns = {
    'PUSH': [
        (re.compile(r'^PUSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_PUSH_T1_A, {}),
    ],
    'STMDB': [
        (re.compile(r'^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_PUSH_T1_A, {}),
    ],
}
