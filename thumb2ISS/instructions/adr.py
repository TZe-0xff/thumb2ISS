#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.ADR')
# instruction aarch32_ADR_A
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   ADD{<c>}{<q>} <Rd>, PC, #<imm8> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T1_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;

    def aarch32_ADR_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T1_A_exec skipped')
    return aarch32_ADR_T1_A_exec

# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   SUB{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T2_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = False;
    if d == 15:
        raise Exception('UNPREDICTABLE');     # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T2_A_exec skipped')
    return aarch32_ADR_T2_A_exec

# pattern ADR{<c>}.W <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   ADDW{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
# alias   ADD{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T3_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;
    if d == 15:
        raise Exception('UNPREDICTABLE');   # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T3_A_exec skipped')
    return aarch32_ADR_T3_A_exec


patterns = {
    'ADR': [
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T1_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T2_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
    ],
    'ADD': [
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T3_A, {'S': '0'}),
    ],
    'SUB': [
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T2_A, {'S': '0'}),
    ],
    'ADDW': [
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T3_A, {'S': '0'}),
    ],
}
