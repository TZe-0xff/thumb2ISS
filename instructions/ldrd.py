import re, logging

log = logging.getLogger('Mnem.LDRD')
# instruction aarch32_LDRD_i_A
# pattern LDRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn> {, #{+/-}<imm>}] with bitdiffs=[('P', '1'), ('W', '0')]
# regex ^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$ : c Rt Rt2 Rn imm32*
# pattern LDRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rt2 Rn imm32
# pattern LDRD{<c>}{<q>} <Rt>, <Rt2>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rt2 Rn imm32
def aarch32_LDRD_i_T1_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRD_i_T1_A Rt={Rt} Rt2={Rt2} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  t2 = core.reg_num[Rt2];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if wback and (n == t or n == t2):
        raise Exception('UNPREDICTABLE');
    if t == 15 or t2 == 15 or t == t2:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRD_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            if core.IsAligned(address, 8):
                data = core.ReadMemA(address,8);
                if core.BigEndian(AccessType_GPR) :
                    core.R[t] = core.Field(data,63,32);
                    core.R[t2] = core.Field(data,31,0);
                else:
                    core.R[t] = core.Field(data,31,0);
                    core.R[t2] = core.Field(data,63,32);
            else:
                core.R[t] = core.ReadMemA(address,4);
                core.R[t2] = core.ReadMemA(address+4,4);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
        else:
            log.debug(f'aarch32_LDRD_i_T1_A_exec skipped')
    return aarch32_LDRD_i_T1_A_exec


# instruction aarch32_LDRD_l_A
# pattern LDRD{<c>}{<q>} <Rt>, <Rt2>, <label> with bitdiffs=[('P', '0'), ('W', '0')]
# regex ^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt Rt2 abs_address
# pattern LDRD{<c>}{<q>} <Rt>, <Rt2>, [PC, #{+/-}<imm>] with bitdiffs=[('P', '0'), ('W', '0')]
# regex ^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt Rt2 imm32
def aarch32_LDRD_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rt2 = regex_groups.get('Rt2', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    P = bitdiffs.get('P', '0')
    W = bitdiffs.get('W', '0')
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDRD_l_T1_A Rt={Rt} Rt2={Rt2} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  t2 = core.reg_num[Rt2];
    add = (U == '1');
    if t == 15 or t2 == 15 or t == t2:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if W == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_LDRD_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if abs_address is None:
                address = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            else:
                address = abs_address;
            if core.IsAligned(address, 8):
                data = core.ReadMemA(address,8);
                if True:
                    core.R[t] = core.Field(data,31,0);
                    core.R[t2] = core.Field(data,63,32);
            else:
                core.R[t] = core.ReadMemA(address,4);
                core.R[t2] = core.ReadMemA(address+4,4);
        else:
            log.debug(f'aarch32_LDRD_l_T1_A_exec skipped')
    return aarch32_LDRD_l_T1_A_exec


patterns = {
    'LDRD': [
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRD_l_T1_A, {'P': '0', 'W': '0'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRD_l_T1_A, {'P': '0', 'W': '0'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$', re.I), aarch32_LDRD_i_T1_A, {'P': '1', 'W': '0'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRD_i_T1_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRD_i_T1_A, {'P': '1', 'W': '1'}),
    ],
}
