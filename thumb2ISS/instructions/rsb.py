import re, logging

log = logging.getLogger('Mnem.RSB')
# instruction aarch32_RSB_i_A
# pattern RSB<c>{<q>} {<Rd>, }<Rn>, #0 with bitdiffs=[('S', '0')]
# regex ^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$ : c Rd* Rn
# pattern RSBS{<q>} {<Rd>, }<Rn>, #0 with bitdiffs=[('S', '1')]
# regex ^RSBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$ : Rd* Rn
# pattern NEG<c>{<q>} {<Rd>,} <Rn> with bitdiffs=[('S', '0')]
# regex ^NEG(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$ : c Rd* Rn
# pattern NEGS{<q>} {<Rd>,} <Rn> with bitdiffs=[('S', '1')]
# regex ^NEGS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$ : Rd* Rn
def aarch32_RSB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_RSB_i_T1_A Rd={Rd} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  imm32 = core.Zeros(32); # immediate = #0

    def aarch32_RSB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.NOT(core.readR(n)), imm32, '1');
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_RSB_i_T1_A_exec skipped')
    return aarch32_RSB_i_T1_A_exec

# pattern RSB<c>.W {<Rd>,} <Rn>, #0 with bitdiffs=[('S', '0')]
# regex ^RSB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$ : c Rd* Rn
# pattern RSB{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern RSBS.W {<Rd>,} <Rn>, #0 with bitdiffs=[('S', '1')]
# regex ^RSBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$ : Rd* Rn
# pattern RSBS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_RSB_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_RSB_i_T2_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_RSB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.NOT(core.readR(n)), imm32, '1');
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_RSB_i_T2_A_exec skipped')
    return aarch32_RSB_i_T2_A_exec


# instruction aarch32_RSB_r_A
# pattern RSB{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern RSB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern RSBS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern RSBS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_RSB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if Rd is None:
        Rd = Rn
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_RSB_r_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_RSB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.NOT(core.readR(n)), shifted, '1');
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_RSB_r_T1_A_exec skipped')
    return aarch32_RSB_r_T1_A_exec


patterns = {
    'RSB': [
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T1_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T2_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_RSB_i_T2_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_RSB_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_RSB_r_T1_A, {'S': '0', 'stype': '11'}),
    ],
    'RSBS': [
        (re.compile(r'^RSBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T1_A, {'S': '1'}),
        (re.compile(r'^RSBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T2_A, {'S': '1'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_RSB_i_T2_A, {'S': '1'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_RSB_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_RSB_r_T1_A, {'S': '1', 'stype': '11'}),
    ],
    'NEG': [
        (re.compile(r'^NEG(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$', re.I), aarch32_RSB_i_T1_A, {'S': '0'}),
    ],
    'NEGS': [
        (re.compile(r'^NEGS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$', re.I), aarch32_RSB_i_T1_A, {'S': '1'}),
    ],
}
