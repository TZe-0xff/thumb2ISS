import re, logging

log = logging.getLogger('Mnem.SMLAD')
# instruction aarch32_SMLAD_A
# pattern SMLAD{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '0')]
# regex ^SMLAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLADX{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '1')]
# regex ^SMLADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLAD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLAD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLAD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.R[m],16) if m_swap else core.R[m];
            product1 = core.SInt(core.Field(core.R[n],15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.R[n],31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 + product2 + core.SInt(core.R[a]);
            core.R[d] = core.Field(result,31,0);
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLAD_T1_A_exec skipped')
    return aarch32_SMLAD_T1_A_exec


patterns = {
    'SMLAD': [
        (re.compile(r'^SMLAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAD_T1_A, {'M': '0'}),
    ],
    'SMLADX': [
        (re.compile(r'^SMLADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAD_T1_A, {'M': '1'}),
    ],
}