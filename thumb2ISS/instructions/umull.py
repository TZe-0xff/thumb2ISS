import re, logging

log = logging.getLogger('Mnem.UMULL')
# instruction aarch32_UMULL_A
# pattern UMULL{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[]
# regex ^UMULL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_UMULL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_UMULL_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = False;
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_UMULL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.UInt(core.readR(n)) * core.UInt(core.readR(m));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,63);
                core.APSR.Z = core.IsZeroBit(core.Field(result,63,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_UMULL_T1_A_exec skipped')
    return aarch32_UMULL_T1_A_exec


patterns = {
    'UMULL': [
        (re.compile(r'^UMULL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UMULL_T1_A, {}),
    ],
}
