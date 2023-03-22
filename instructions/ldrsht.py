import re, logging

log = logging.getLogger('Mnem.LDRSHT')
# instruction aarch32_LDRSHT_A
# pattern LDRSHT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRSHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRSHT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRSHT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSHT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.R[m] if register_form else imm32;
            offset_addr = (core.R[n] + offset) if add else (core.R[n] - offset);
            address = core.R[n] if postindex else offset_addr;
            data = MemU_unpriv[address,2];
            if postindex:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSHT_T1_A_exec skipped')
    return aarch32_LDRSHT_T1_A_exec


patterns = {
    'LDRSHT': [
        (re.compile(r'^LDRSHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSHT_T1_A, {}),
    ],
}
