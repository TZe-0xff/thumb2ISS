import re, logging

log = logging.getLogger('Mnem.SMLALBB')
# instruction aarch32_SMLALBB_A
# pattern SMLALBB{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMLALBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALBT{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMLALBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALTB{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMLALTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALTT{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMLALTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLALBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLALBB_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    n_high = (N == '1');  m_high = (M == '1');
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLALBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.R[n],31,16) if n_high else core.Field(core.R[n],15,0);
            operand2 = core.Field(core.R[m],31,16) if m_high else core.Field(core.R[m],15,0);
            result = core.SInt(operand1) * core.SInt(operand2) + core.SInt(core.R[dLo], core.R[dHi]);
            core.R[dHi] = core.Field(result,63,32);
            core.R[dLo] = core.Field(result,31,0);
        else:
            log.debug(f'aarch32_SMLALBB_T1_A_exec skipped')
    return aarch32_SMLALBB_T1_A_exec


patterns = {
    'SMLALBB': [
        (re.compile(r'^SMLALBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMLALBT': [
        (re.compile(r'^SMLALBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMLALTB': [
        (re.compile(r'^SMLALTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMLALTT': [
        (re.compile(r'^SMLALTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '1', 'M': '1'}),
    ],
}
