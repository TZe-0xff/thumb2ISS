import re, logging

log = logging.getLogger('Mnem.LDRSH')
# instruction aarch32_LDRSH_i_A
# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRSH_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRSH_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSH_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSH_i_T1_A_exec skipped')
    return aarch32_LDRSH_i_T1_A_exec

# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_LDRSH_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    P = bitdiffs.get('P', '0')
    U = bitdiffs.get('U', '1')
    W = bitdiffs.get('W', '0')
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRSH_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if P == '0' and W == '0':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if (t == 15 and W == '1') or (wback and n == t):
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSH_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSH_i_T2_A_exec skipped')
    return aarch32_LDRSH_i_T2_A_exec


# instruction aarch32_LDRSH_l_A
# pattern LDRSH{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDRSH{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt imm32
def aarch32_LDRSH_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDRSH_l_T1_A Rt={Rt} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = (U == '1');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSH_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            if abs_address is None:
                address = (base + imm32) if add else (base - imm32);
            else:
                address = abs_address;
            data = core.ReadMemU(address,2);
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSH_l_T1_A_exec skipped')
    return aarch32_LDRSH_l_T1_A_exec


# instruction aarch32_LDRSH_r_A
# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_LDRSH_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_LDRSH_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_LDRSH_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSH_r_T1_A_exec skipped')
    return aarch32_LDRSH_r_T1_A_exec

# pattern LDRSH{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern LDRSH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_LDRSH_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_LDRSH_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSH_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.R[n] = offset_addr; log.info(f'Setting R{n}={hex(core.UInt(core.Field(offset_addr)))}')
            core.R[t] = core.SignExtend(data, 32);
        else:
            log.debug(f'aarch32_LDRSH_r_T2_A_exec skipped')
    return aarch32_LDRSH_r_T2_A_exec


patterns = {
    'LDRSH': [
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRSH_l_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRSH_l_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSH_i_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDRSH_i_T2_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRSH_i_T2_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRSH_i_T2_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSH_r_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSH_r_T2_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDRSH_r_T2_A, {}),
    ],
}
