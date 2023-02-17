import re, logging

log = logging.getLogger('Mnem.ADC')
# instruction aarch32_ADC_i_A
# pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ADC_i_T1_A(core, regex_match, bitdiffs):
    cond = regex_match.group('c')
    Rd = regex_match.group('Rd')
    Rn = regex_match.group('Rn')
    imm32 = regex_match.group('imm32')
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ADC_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE');  # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADC_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], imm32, core.APSR.C);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADC_i_T1_A_exec skipped')
    return aarch32_ADC_i_T1_A_exec


# instruction aarch32_ADC_r_A
# pattern ADC<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ADCS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[]
# regex ^ADCS(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_ADC_r_T1_A(core, regex_match, bitdiffs):
    cond = regex_match.group('c')
    Rdn = regex_match.group('Rdn')
    Rm = regex_match.group('Rm')
    log.debug(f'aarch32_ADC_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.UInt(Rdn);  n = core.UInt(Rdn);  m = core.reg_num[Rm];  setflags = not core.InITBlock();
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ADC_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], shifted, core.APSR.C);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADC_r_T1_A_exec skipped')
    return aarch32_ADC_r_T1_A_exec

# pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ADC<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ADCS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADCS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_ADC_r_T2_A(core, regex_match, bitdiffs):
    cond = regex_match.group('c')
    Rd = regex_match.group('Rd')
    Rn = regex_match.group('Rn')
    Rm = regex_match.group('Rm')
    shift_t = regex_match.group('shift_t')
    shift_n = regex_match.group('shift_n')
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if Rd is None:
        Rd = Rn
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_ADC_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADC_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], shifted, core.APSR.C);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADC_r_T2_A_exec skipped')
    return aarch32_ADC_r_T2_A_exec


patterns = {
    'ADC': [
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADC_i_T1_A, {'S': '0'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'ADCS': [
        (re.compile(r'^ADCS(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADC_i_T1_A, {'S': '1'}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'ADCS.W ': [
        (re.compile(r'^ADCS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
}


if __name__ == '__main__':
    from _testing import Core, test
    logging.basicConfig(level=logging.DEBUG)
    c = Core()

    steps = []
    steps += [c.getExec('adc', 'r0, #10', 0)]
    steps += [c.getExec('adcs', 'r1, r0, #10', 0)]
    steps += [c.getExec('adcs', 'r1, #1', 0)]
    steps += [c.getExec('adcs', 'r1, r0', 0)]
    steps += [c.getExec('adc', 'r2, r1, r0', 0)]

    test(c, steps)
