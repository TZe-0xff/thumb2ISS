#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import re, logging

log = logging.getLogger('Mnem.TBB')
# instruction aarch32_TBB_A
# pattern TBB{<c>}{<q>} [<Rn>, <Rm>] with bitdiffs=[('H', '0')]
# regex ^TBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+)\]$ : c Rn Rm
# pattern TBH{<c>}{<q>} [<Rn>, <Rm>, LSL #1] with bitdiffs=[('H', '1')]
# regex ^TBH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+),\sLSL\s#1\]$ : c Rn Rm
def aarch32_TBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    H = bitdiffs.get('H', '0')
    log.debug(f'aarch32_TBB_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];  is_tbh = (H == '1');
    if m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_TBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            halfwords = 0;
            if is_tbh:
                halfwords = core.UInt(core.ReadMemU(core.readR(n)+core.LSL(core.readR(m),1), 2));
            else:
                halfwords = core.UInt(core.ReadMemU(core.readR(n)+core.readR(m), 1));
            core.BranchWritePC(core.PC + 2*halfwords, 'INDIR');
        else:
            log.debug(f'aarch32_TBB_T1_A_exec skipped')
    return aarch32_TBB_T1_A_exec


patterns = {
    'TBB': [
        (re.compile(r'^TBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+)\]$', re.I), aarch32_TBB_T1_A, {'H': '0'}),
    ],
    'TBH': [
        (re.compile(r'^TBH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+),\sLSL\s#1\]$', re.I), aarch32_TBB_T1_A, {'H': '1'}),
    ],
}
