import re, logging

log = logging.getLogger('Mnem.STRD')
# instruction aarch32_STRD_i_A
# pattern STRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn> {, #{+/-}<imm>}] with bitdiffs=[('P', '1'), ('W', '0')]
# regex ^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$ : c Rt Rt2 Rn imm32*
# pattern STRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rt2 Rn imm32
# pattern STRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rt2 Rn imm32
def aarch32_STRD_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rt2 = regex_groups.get('Rt2', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    P = bitdiffs.get('P', '0')
    W = bitdiffs.get('W', '0')
    U = bitdiffs.get('U', '1')
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRD_i_T1_A Rt={Rt} Rt2={Rt2} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  t2 = core.reg_num[Rt2];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if wback and (n == t or n == t2):
        raise Exception('UNPREDICTABLE');
    if n == 15 or t == 15 or t2 == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRD_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.R[n] + imm32) if add else (core.R[n] - imm32);
            address = offset_addr if index else core.R[n];
            if core.IsAligned(address, 8):
                data = 0;
                if True:
                    data = core.SetField(data,31,0,core.R[t]);
                    data = core.SetField(data,63,32,core.R[t2]);
                core.WriteMemA(address,8, data);
            else:
                core.WriteMemA(address,4, core.R[t]);
                core.WriteMemA(address+4,4, core.R[t2]);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(offset_addr))}')
        else:
            log.debug(f'aarch32_STRD_i_T1_A_exec skipped')
    return aarch32_STRD_i_T1_A_exec


patterns = {
    'STRD': [
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$', re.I), aarch32_STRD_i_T1_A, {'P': '1', 'W': '0'}),
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_STRD_i_T1_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_STRD_i_T1_A, {'P': '1', 'W': '1'}),
    ],
}
