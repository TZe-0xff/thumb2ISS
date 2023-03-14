import re, logging

log = logging.getLogger('Mnem.AND')
# instruction aarch32_AND_i_A
# pattern AND{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ANDS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_AND_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_AND_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if (d == 15 and not setflags) or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_AND_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.R[n] & imm32;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = core.Field(result); log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_AND_i_T1_A_exec skipped')
    return aarch32_AND_i_T1_A_exec


# instruction aarch32_AND_r_A
# pattern AND<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ANDS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[]
# regex ^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_AND_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_AND_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = not (cond is not None);
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_AND_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = core.R[n] & shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = core.Field(result); log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_AND_r_T1_A_exec skipped')
    return aarch32_AND_r_T1_A_exec

# pattern AND{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern AND<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern AND{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern ANDS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ANDS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ANDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern ANDS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_AND_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_AND_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_AND_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            result = core.R[n] & shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = core.Field(result); log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_AND_r_T2_A_exec skipped')
    return aarch32_AND_r_T2_A_exec


patterns = {
    'AND': [
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_AND_i_T1_A, {'S': '0'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'ANDS': [
        (re.compile(r'^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {}),
        (re.compile(r'^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {}),
        (re.compile(r'^ANDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_AND_i_T1_A, {'S': '1'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
}
