import re, logging

log = logging.getLogger('Mnem.LDRBT')
# instruction aarch32_LDRBT_A
# pattern LDRBT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRBT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRBT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRBT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C) if register_form else imm32;
            offset_addr = (core.R[n] + offset) if add else (core.R[n] - offset);
            address = core.R[n] if postindex else offset_addr;
            core.R[t] = core.ZeroExtend(MemU_unpriv[address,1],32);
            if postindex:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(offset_addr))}')
        else:
            log.debug(f'aarch32_LDRBT_T1_A_exec skipped')
    return aarch32_LDRBT_T1_A_exec


patterns = {
    'LDRBT': [
        (re.compile(r'^LDRBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRBT_T1_A, {}),
    ],
}
