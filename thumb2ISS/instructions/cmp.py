#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.CMP')
# instruction aarch32_CMP_i_A
# pattern CMP{<c>}{<q>} <Rn>, #<imm8> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMP_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMP_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  

    def aarch32_CMP_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_i_T1_A_exec skipped')
    return aarch32_CMP_i_T1_A_exec

# pattern CMP{<c>}.W <Rn>, #<const> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
# pattern CMP{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMP_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMP_i_T2_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMP_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_i_T2_A_exec skipped')
    return aarch32_CMP_i_T2_A_exec


# instruction aarch32_CMP_r_A
# pattern CMP{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMP_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMP_r_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_CMP_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T1_A_exec skipped')
    return aarch32_CMP_r_T1_A_exec

# pattern CMP{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMP_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMP_r_T2_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);
    if n < 8 and m < 8:
        raise Exception('UNPREDICTABLE');
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMP_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T2_A_exec skipped')
    return aarch32_CMP_r_T2_A_exec

# pattern CMP{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern CMP{<c>}.W <Rn>, <Rm> with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
# pattern CMP{<c>}{<q>} <Rn>, <Rm>, <shift> #<amount> with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+)$ : c Rn Rm shift_t shift_n
def aarch32_CMP_r_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    log.debug(f'aarch32_CMP_r_T3_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CMP_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T3_A_exec skipped')
    return aarch32_CMP_r_T3_A_exec


patterns = {
    'CMP': [
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T1_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T1_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
    ],
}
