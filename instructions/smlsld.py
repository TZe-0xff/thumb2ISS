import re, logging

log = logging.getLogger('Mnem.SMLSLD')
# instruction aarch32_SMLSLD_A
# pattern SMLSLD{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMLSLD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLSLDX{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMLSLDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLSLD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLSLD_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes UPREDICTABLE for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLSLD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.R[m],16) if m_swap else core.R[m];
            product1 = core.SInt(core.Field(core.R[n],15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.R[n],31,16)) * core.SInt(core.Field(operand2,31,16));
            result = (product1 - product2) + core.SInt(core.R[dLo], core.R[dHi]);
            core.R[dHi] = core.Field(result,63,32);
            core.R[dLo] = core.Field(result,31,0);
        else:
            log.debug(f'aarch32_SMLSLD_T1_A_exec skipped')
    return aarch32_SMLSLD_T1_A_exec


patterns = {
    'SMLSLD': [
        (re.compile(r'^SMLSLD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLSLD_T1_A, {'M': '0'}),
    ],
    'SMLSLDX': [
        (re.compile(r'^SMLSLDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLSLD_T1_A, {'M': '1'}),
    ],
}
