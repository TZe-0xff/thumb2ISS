import re, logging

log = logging.getLogger('Mnem.UMAAL')
# instruction aarch32_UMAAL_A
# pattern UMAAL{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[]
# regex ^UMAAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_UMAAL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_UMAAL_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_UMAAL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.UInt(core.readR(n)) * core.UInt(core.readR(m)) + core.UInt(core.readR(dHi)) + core.UInt(core.readR(dLo));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_UMAAL_T1_A_exec skipped')
    return aarch32_UMAAL_T1_A_exec


patterns = {
    'UMAAL': [
        (re.compile(r'^UMAAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UMAAL_T1_A, {}),
    ],
}
