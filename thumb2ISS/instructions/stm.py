#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.STM')
# instruction aarch32_STM_A
# pattern STM{IA}{<c>}{<q>} <Rn>!, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# pattern STMEA{<c>}{<q>} <Rn>!, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
def aarch32_STM_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_STM_T1_A Rn={Rn} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  wback = True;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_STM_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encodings T1 and A1
                    else:
                        core.WriteMemS(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
        else:
            log.debug(f'aarch32_STM_T1_A_exec skipped')
    return aarch32_STM_T1_A_exec

# pattern STM{IA}{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STMEA{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STM{IA}{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STMEA{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_STM_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    W = bitdiffs.get('W', '0')
    log.debug(f'aarch32_STM_T2_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15 or registers.count('1') < 2:
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[15] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_STM_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encodings T1 and A1
                    else:
                        core.WriteMemS(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
        else:
            log.debug(f'aarch32_STM_T2_A_exec skipped')
    return aarch32_STM_T2_A_exec


patterns = {
    'STM': [
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T1_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
    ],
    'STMEA': [
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T1_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
    ],
}
