import re, logging

log = logging.getLogger('Mnem.All')
# instruction aarch32_ADC_i_A
# pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ADC_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
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
            (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, core.APSR.C);
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
            log.debug(f'aarch32_ADC_i_T1_A_exec skipped')
    return aarch32_ADC_i_T1_A_exec


# instruction aarch32_ADC_r_A
# pattern ADC<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ADCS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^ADCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^ADCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_ADC_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_ADC_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ADC_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, core.APSR.C);
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
    log.debug(f'aarch32_ADC_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADC_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, core.APSR.C);
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
            log.debug(f'aarch32_ADC_r_T2_A_exec skipped')
    return aarch32_ADC_r_T2_A_exec


# instruction aarch32_ADD_i_A
# pattern ADD<c>{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd Rn imm32
# pattern ADDS{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[('S', '1')]
# regex ^ADDS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : Rd Rn imm32
def aarch32_ADD_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_ADD_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  

    def aarch32_ADD_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, '0');
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_i_T1_A_exec skipped')
    return aarch32_ADD_i_T1_A_exec

# pattern ADD<c>{<q>} <Rdn>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern ADD<c>{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$ : c Rdn imm32
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern ADDS{<q>} <Rdn>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
# pattern ADDS{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$ : Rdn imm32
# regex ^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
def aarch32_ADD_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_ADD_i_T2_A Rdn={Rdn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  setflags = (S == '1');  

    def aarch32_ADD_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, '0');
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_i_T2_A_exec skipped')
    return aarch32_ADD_i_T2_A_exec

# pattern ADD<c>.W {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ADD{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ADDS.W {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : Rd* Rn imm32
# pattern ADDS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ADD_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ADD_i_T3_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  
    if (d == 15 and not setflags) or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADD_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, '0');
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_i_T3_A_exec skipped')
    return aarch32_ADD_i_T3_A_exec

# pattern ADD{<c>}{<q>} {<Rd>,} <Rn>, #<imm12> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ADDW{<c>}{<q>} {<Rd>,} <Rn>, #<imm12> with bitdiffs=[]
# regex ^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ADD_i_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ADD_i_T4_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE');   # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADD_i_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, '0');
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_i_T4_A_exec skipped')
    return aarch32_ADD_i_T4_A_exec


# instruction aarch32_ADD_r_A
# pattern ADD<c>{<q>} <Rd>, <Rn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd Rn Rm
# pattern ADDS{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^ADDS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
def aarch32_ADD_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ADD_r_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ADD_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_r_T1_A_exec skipped')
    return aarch32_ADD_r_T1_A_exec

# pattern ADD<c>{<q>} <Rdn>, <Rm> with bitdiffs=[('DN', '1')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ADD{<c>}{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('DN', '1')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
def aarch32_ADD_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    DN = bitdiffs.get('DN', '0')
    log.debug(f'aarch32_ADD_r_T2_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = d;  m = core.reg_num[Rm];  setflags = False;  (shift_t, shift_n) = ('LSL', 0);
    if n == 15 and m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_ADD_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_r_T2_A_exec skipped')
    return aarch32_ADD_r_T2_A_exec

# pattern ADD{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ADD<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern ADD{<c>}.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern ADD{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern ADDS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ADDS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern ADDS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_ADD_r_T3_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_ADD_r_T3_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADD_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_r_T3_A_exec skipped')
    return aarch32_ADD_r_T3_A_exec


# instruction aarch32_ADD_SP_i_A
# pattern ADD{<c>}{<q>} <Rd>, SP, #<imm8> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sSP,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADD_SP_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADD_SP_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = False;  

    def aarch32_ADD_SP_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), imm32, '0');
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
            log.debug(f'aarch32_ADD_SP_i_T1_A_exec skipped')
    return aarch32_ADD_SP_i_T1_A_exec

# pattern ADD{<c>}{<q>} {SP,} SP, #<imm7> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$ : c imm32
def aarch32_ADD_SP_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADD_SP_i_T2_A imm32={imm32} cond={cond}')
    # decode
    d = 13;  setflags = False;  

    def aarch32_ADD_SP_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), imm32, '0');
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
            log.debug(f'aarch32_ADD_SP_i_T2_A_exec skipped')
    return aarch32_ADD_SP_i_T2_A_exec

# pattern ADD{<c>}.W {<Rd>,} SP, #<const> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern ADD{<c>}{<q>} {<Rd>,} SP, #<const> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern ADDS{<c>}{<q>} {<Rd>,} SP, #<const> with bitdiffs=[('S', '1')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
def aarch32_ADD_SP_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_ADD_SP_i_T3_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  
    if d == 15 and not setflags:
        raise Exception('UNPREDICTABLE');

    def aarch32_ADD_SP_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), imm32, '0');
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
            log.debug(f'aarch32_ADD_SP_i_T3_A_exec skipped')
    return aarch32_ADD_SP_i_T3_A_exec

# pattern ADD{<c>}{<q>} {<Rd>,} SP, #<imm12> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern ADDW{<c>}{<q>} {<Rd>,} SP, #<imm12> with bitdiffs=[]
# regex ^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
def aarch32_ADD_SP_i_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADD_SP_i_T4_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_ADD_SP_i_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), imm32, '0');
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
            log.debug(f'aarch32_ADD_SP_i_T4_A_exec skipped')
    return aarch32_ADD_SP_i_T4_A_exec


# instruction aarch32_ADD_SP_r_A
# pattern ADD{<c>}{<q>} {<Rdm>,} SP, <Rdm> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\sSP,\s(?P=Rdm)$ : c Rdm
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP,\s(?P<Rdm>\w+)$ : c Rdm
def aarch32_ADD_SP_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    log.debug(f'aarch32_ADD_SP_r_T1_A Rdm={Rdm} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  m = core.reg_num[Rdm];  setflags = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ADD_SP_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(13), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_SP_r_T1_A_exec skipped')
    return aarch32_ADD_SP_r_T1_A_exec

# pattern ADD{<c>}{<q>} {SP,} SP, <Rm> with bitdiffs=[]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s(?P<Rm>\w+)$ : c Rm
def aarch32_ADD_SP_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_ADD_SP_r_T2_A Rm={Rm} cond={cond}')
    # decode
    d = 13;  m = core.reg_num[Rm];  setflags = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ADD_SP_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(13), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_SP_r_T2_A_exec skipped')
    return aarch32_ADD_SP_r_T2_A_exec

# pattern ADD{<c>}{<q>} {<Rd>,} SP, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rm shift_t
# pattern ADD{<c>}.W {<Rd>,} SP, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$ : c Rd* Rm
# pattern ADD{<c>}{<q>} {<Rd>,} SP, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rm shift_t* shift_n*
# pattern ADDS{<c>}{<q>} {<Rd>,} SP, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rm shift_t
# pattern ADDS{<c>}{<q>} {<Rd>,} SP, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rm shift_t* shift_n*
def aarch32_ADD_SP_r_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_ADD_SP_r_T3_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADD_SP_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(13), shifted, '0');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_ADD_SP_r_T3_A_exec skipped')
    return aarch32_ADD_SP_r_T3_A_exec


# instruction aarch32_ADR_A
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   ADD{<c>}{<q>} <Rd>, PC, #<imm8> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T1_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;

    def aarch32_ADR_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T1_A_exec skipped')
    return aarch32_ADR_T1_A_exec

# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   SUB{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T2_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = False;
    if d == 15:
        raise Exception('UNPREDICTABLE');     # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T2_A_exec skipped')
    return aarch32_ADR_T2_A_exec

# pattern ADR{<c>}.W <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# alias   ADDW{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
# alias   ADD{<c>}{<q>} <Rd>, PC, #<imm12> with bitdiffs=[('S', '0')]
# regex ^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_ADR_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_ADR_T3_A Rd={Rd} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;
    if d == 15:
        raise Exception('UNPREDICTABLE');   # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_ADR_T3_A_exec skipped')
    return aarch32_ADR_T3_A_exec


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
            result = core.readR(n) & imm32;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_AND_i_T1_A_exec skipped')
    return aarch32_AND_i_T1_A_exec


# instruction aarch32_AND_r_A
# pattern AND<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ANDS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_AND_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_AND_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_AND_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
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
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_AND_r_T2_A_exec skipped')
    return aarch32_AND_r_T2_A_exec


# instruction aarch32_B_A
# pattern B<c>{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T1_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T1_A_exec skipped')
    return aarch32_B_T1_A_exec

# pattern B{<c>}{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T2_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T2_A_exec skipped')
    return aarch32_B_T2_A_exec

# pattern B<c>.W <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
# pattern B<c>{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T3_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T3_A_exec skipped')
    return aarch32_B_T3_A_exec

# pattern B{<c>}.W <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
# pattern B{<c>}{<q>} <label> with bitdiffs=[]
# regex ^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_B_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_B_T4_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_B_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BranchWritePC(abs_address, 'DIR');
        else:
            log.debug(f'aarch32_B_T4_A_exec skipped')
    return aarch32_B_T4_A_exec


# instruction aarch32_BFC_A
# pattern BFC{<c>}{<q>} <Rd>, #<lsb>, #<width> with bitdiffs=[]
# regex ^BFC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd lsb width
def aarch32_BFC_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_BFC_T1_A Rd={Rd} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  msbit = core.UInt(width) - 1 + core.UInt(lsb);  lsbit = core.UInt(lsb);
    if d == 15:
        raise Exception('UNPREDICTABLE');  # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit < lsbit:
        raise Exception('UNPREDICTABLE');

    def aarch32_BFC_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.readR(d) & ~((0xffffffff >> (31 - msbit + lsbit)) << lsbit));
            # Other bits of core.readR(d) are unchanged
        else:
            log.debug(f'aarch32_BFC_T1_A_exec skipped')
    return aarch32_BFC_T1_A_exec


# instruction aarch32_BFI_A
# pattern BFI{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_BFI_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_BFI_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  msbit = core.UInt(width) - 1 + core.UInt(lsb);  lsbit = core.UInt(lsb);
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit < lsbit:
        raise Exception('UNPREDICTABLE');

    def aarch32_BFI_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            mask = 0xffffffff >> (31 - msbit + lsbit);
            tmp_Rd = core.readR(d) & ~((mask) << lsbit);
            core.writeR(d, tmp_Rd | ((core.UInt(core.readR(n)) & mask) << lsbit));
            # Other bits of core.readR(d) are unchanged
        else:
            log.debug(f'aarch32_BFI_T1_A_exec skipped')
    return aarch32_BFI_T1_A_exec


# instruction aarch32_BIC_i_A
# pattern BIC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern BICS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_BIC_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_BIC_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE');  # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_BIC_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) & core.NOT(imm32);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_BIC_i_T1_A_exec skipped')
    return aarch32_BIC_i_T1_A_exec


# instruction aarch32_BIC_r_A
# pattern BIC<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern BICS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^BICS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^BICS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_BIC_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_BIC_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_BIC_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_BIC_r_T1_A_exec skipped')
    return aarch32_BIC_r_T1_A_exec

# pattern BIC{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern BIC<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern BIC{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern BICS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern BICS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^BICS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern BICS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_BIC_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_BIC_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');  # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_BIC_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_BIC_r_T2_A_exec skipped')
    return aarch32_BIC_r_T2_A_exec


# instruction aarch32_BKPT_A
# pattern BKPT{<q>} {#}<imm> with bitdiffs=[]
# regex ^BKPT(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : imm32
def aarch32_BKPT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_BKPT_T1_A imm32={imm32}')
    # decode

    def aarch32_BKPT_T1_A_exec():
        # execute
        core.SoftwareBreakpoint(imm32);
    return aarch32_BKPT_T1_A_exec


# instruction aarch32_BLX_r_A
# pattern BLX{<c>}{<q>} <Rm> with bitdiffs=[]
# regex ^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$ : c Rm
def aarch32_BLX_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_BLX_r_T1_A Rm={Rm} cond={cond}')
    # decode
    m = core.reg_num[Rm];
    if m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_BLX_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            target = core.readR(m);
            core.BXWritePC(target, 'INDCALL');
        else:
            log.debug(f'aarch32_BLX_r_T1_A_exec skipped')
    return aarch32_BLX_r_T1_A_exec


# instruction aarch32_BL_i_A
# pattern BL{<c>}{<q>} <label> with bitdiffs=[]
# regex ^BL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_BL_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_BL_i_T1_A abs_address={hex(abs_address)} cond={cond}')
    # decode

    def aarch32_BL_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                targetAddress = abs_address;
            core.BranchWritePC(targetAddress, 'DIRCALL');
        else:
            log.debug(f'aarch32_BL_i_T1_A_exec skipped')
    return aarch32_BL_i_T1_A_exec

# pattern BLX{<c>}{<q>} <label> with bitdiffs=[]
# regex ^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$ : c abs_address
def aarch32_BL_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    H = bitdiffs.get('H', '0')
    log.debug(f'aarch32_BL_i_T2_A abs_address={hex(abs_address)} cond={cond}')
    # decode
    if H == '1':
        raise Exception('UNDEFINED');

    def aarch32_BL_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                targetAddress = abs_address;
            core.BranchWritePC(targetAddress, 'DIRCALL');
        else:
            log.debug(f'aarch32_BL_i_T2_A_exec skipped')
    return aarch32_BL_i_T2_A_exec


# instruction aarch32_BX_A
# pattern BX{<c>}{<q>} <Rm> with bitdiffs=[]
# regex ^BX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$ : c Rm
def aarch32_BX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_BX_T1_A Rm={Rm} cond={cond}')
    # decode
    m = core.reg_num[Rm];

    def aarch32_BX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.BXWritePC(core.readR(m), 'INDIR');
        else:
            log.debug(f'aarch32_BX_T1_A_exec skipped')
    return aarch32_BX_T1_A_exec


# instruction aarch32_CBNZ_A
# pattern CBNZ{<q>} <Rn>, <label> with bitdiffs=[('op', '1')]
# regex ^CBNZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : Rn abs_address
# pattern CBZ{<q>} <Rn>, <label> with bitdiffs=[('op', '0')]
# regex ^CBZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : Rn abs_address
def aarch32_CBNZ_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    Rn = regex_groups.get('Rn', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    op = bitdiffs.get('op', '0')
    log.debug(f'aarch32_CBNZ_T1_A Rn={Rn} abs_address={hex(abs_address)}')
    # decode
    n = core.reg_num[Rn];  nonzero = (op == '1');

    def aarch32_CBNZ_T1_A_exec():
        # execute
        if nonzero != core.IsZero(core.readR(n)):
            core.CBWritePC(abs_address);
    return aarch32_CBNZ_T1_A_exec


# instruction aarch32_CLREX_A
# pattern CLREX{<c>}{<q>} with bitdiffs=[]
# regex ^CLREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$ : c
def aarch32_CLREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_CLREX_T1_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_CLREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.ClearExclusiveLocal(core.ProcessorID());
        else:
            log.debug(f'aarch32_CLREX_T1_A_exec skipped')
    return aarch32_CLREX_T1_A_exec


# instruction aarch32_CLZ_A
# pattern CLZ{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^CLZ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_CLZ_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = Rm
    log.debug(f'aarch32_CLZ_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CLZ_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.CountLeadingZeroBits(core.readR(m));
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_CLZ_T1_A_exec skipped')
    return aarch32_CLZ_T1_A_exec


# instruction aarch32_CMN_i_A
# pattern CMN{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMN_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), imm32, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_i_T1_A_exec skipped')
    return aarch32_CMN_i_T1_A_exec


# instruction aarch32_CMN_r_A
# pattern CMN{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMN_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMN_r_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_CMN_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_r_T1_A_exec skipped')
    return aarch32_CMN_r_T1_A_exec

# pattern CMN{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern CMN{<c>}.W <Rn>, <Rm> with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
# pattern CMN{<c>}{<q>} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('stype', '11')]
# regex ^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rn Rm shift_t* shift_n*
def aarch32_CMN_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_CMN_r_T2_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CMN_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), shifted, '0');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMN_r_T2_A_exec skipped')
    return aarch32_CMN_r_T2_A_exec


# instruction aarch32_CMP_i_A
# pattern CMP{<c>}{<q>} <Rn>, #<imm8> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMP_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMP_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  

    def aarch32_CMP_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_i_T1_A_exec skipped')
    return aarch32_CMP_i_T1_A_exec

# pattern CMP{<c>}.W <Rn>, #<const> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
# pattern CMP{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_CMP_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_CMP_i_T2_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMP_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_i_T2_A_exec skipped')
    return aarch32_CMP_i_T2_A_exec


# instruction aarch32_CMP_r_A
# pattern CMP{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMP_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMP_r_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_CMP_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T1_A_exec skipped')
    return aarch32_CMP_r_T1_A_exec

# pattern CMP{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_CMP_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_CMP_r_T2_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);
    if n < 8 and m < 8:
        raise Exception('UNPREDICTABLE');
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_CMP_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T2_A_exec skipped')
    return aarch32_CMP_r_T2_A_exec

# pattern CMP{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern CMP{<c>}.W <Rn>, <Rm> with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
# pattern CMP{<c>}{<q>} <Rn>, <Rm>, <shift> #<amount> with bitdiffs=[('stype', '11')]
# regex ^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+)$ : c Rn Rm shift_t shift_n
def aarch32_CMP_r_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    log.debug(f'aarch32_CMP_r_T3_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_CMP_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
            core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_CMP_r_T3_A_exec skipped')
    return aarch32_CMP_r_T3_A_exec


# instruction aarch32_EOR_i_A
# pattern EOR{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern EORS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_EOR_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_EOR_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if (d == 15 and not setflags) or n == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_EOR_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) ^ imm32;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_EOR_i_T1_A_exec skipped')
    return aarch32_EOR_i_T1_A_exec


# instruction aarch32_EOR_r_A
# pattern EOR<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern EORS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^EORS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^EORS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_EOR_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_EOR_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_EOR_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) ^ shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_EOR_r_T1_A_exec skipped')
    return aarch32_EOR_r_T1_A_exec

# pattern EOR{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern EOR<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern EOR{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern EORS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern EORS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^EORS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern EORS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_EOR_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_EOR_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_EOR_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) ^ shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_EOR_r_T2_A_exec skipped')
    return aarch32_EOR_r_T2_A_exec


# instruction aarch32_IT_A
# pattern IT{<x>{<y>{<z>}}}{<q>} <cond> with bitdiffs=[]
# regex ^IT(?P<mask>[ET]*)(?:\.[NW])?\s(?P<firstcond>\w\w)$ : mask firstcond
def aarch32_IT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    mask = regex_groups.get('mask', None)
    firstcond = regex_groups.get('firstcond', None)
    log.debug(f'aarch32_IT_T1_A mask={mask} firstcond={firstcond}')
    # decode

    def aarch32_IT_T1_A_exec():
        # execute
        core.CheckITEnabled(mask);
        core.APSR.ITcond = firstcond; core.APSR.ITsteps = len(mask)
        ShouldAdvanceIT = False;
    return aarch32_IT_T1_A_exec


# instruction aarch32_LDM_A
# pattern LDM{IA}{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern LDMFD{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_LDM_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    log.debug(f'aarch32_LDM_T1_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_LDM_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.writeR(i, core.ReadMemS(address,4));  address = address + 4;
            if registers[15] == '1':
                core.LoadWritePC(core.ReadMemS(address,4));
            if wback and registers[n] == '0':
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
            if wback and registers[n] == '1':
                 core.writeR(n, UNKNOWN = 0);
        else:
            log.debug(f'aarch32_LDM_T1_A_exec skipped')
    return aarch32_LDM_T1_A_exec

# pattern LDM{IA}{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern LDMFD{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern LDM{IA}{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern LDMFD{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_LDM_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    W = bitdiffs.get('W', '0')
    P = bitdiffs.get('P', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_LDM_T2_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15 or registers.count('1') < 2 or (P == '1' and M == '1'):
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_LDM_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.writeR(i, core.ReadMemS(address,4));  address = address + 4;
            if registers[15] == '1':
                core.LoadWritePC(core.ReadMemS(address,4));
            if wback and registers[n] == '0':
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
            if wback and registers[n] == '1':
                 core.writeR(n, UNKNOWN = 0);
        else:
            log.debug(f'aarch32_LDM_T2_A_exec skipped')
    return aarch32_LDM_T2_A_exec


# instruction aarch32_LDMDB_A
# pattern LDMDB{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern LDMEA{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_LDMDB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    W = bitdiffs.get('W', '0')
    P = bitdiffs.get('P', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_LDMDB_T1_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15 or registers.count('1') < 2 or (P == '1' and M == '1'):
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_LDMDB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.writeR(i, core.ReadMemS(address,4));  address = address + 4;
            if registers[15] == '1':
                core.LoadWritePC(core.ReadMemS(address,4));
            if wback and registers[n] == '0':
                 core.writeR(n, core.readR(n) - 4*registers.count('1'));
            if wback and registers[n] == '1':
                 core.writeR(n, UNKNOWN = 0);
        else:
            log.debug(f'aarch32_LDMDB_T1_A_exec skipped')
    return aarch32_LDMDB_T1_A_exec


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
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            core.writeR(t, core.ZeroExtend(MemU_unpriv[address,1],32));
            if postindex:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRBT_T1_A_exec skipped')
    return aarch32_LDRBT_T1_A_exec


# instruction aarch32_LDRB_i_A
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRB_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_LDRB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1), 32));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRB_i_T1_A_exec skipped')
    return aarch32_LDRB_i_T1_A_exec

# pattern LDRB{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRB_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRB_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1), 32));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRB_i_T2_A_exec skipped')
    return aarch32_LDRB_i_T2_A_exec

# pattern LDRB{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_LDRB_i_T3_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRB_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if P == '0' and W == '0':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if  (t == 15 and  W == '1') or (wback and n == t):
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRB_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1), 32));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRB_i_T3_A_exec skipped')
    return aarch32_LDRB_i_T3_A_exec


# instruction aarch32_LDRB_l_A
# pattern LDRB{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDRB{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt imm32
def aarch32_LDRB_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDRB_l_T1_A Rt={Rt} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = (U == '1');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRB_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            if abs_address is None:
                address = (base + imm32) if add else (base - imm32);
            else:
                address = abs_address;
            core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1), 32));
        else:
            log.debug(f'aarch32_LDRB_l_T1_A_exec skipped')
    return aarch32_LDRB_l_T1_A_exec


# instruction aarch32_LDRB_r_A
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_LDRB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_LDRB_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_LDRB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1),32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRB_r_T1_A_exec skipped')
    return aarch32_LDRB_r_T1_A_exec

# pattern LDRB{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern LDRB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_LDRB_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRB_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRB_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.ZeroExtend(core.ReadMemU(address,1),32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRB_r_T2_A_exec skipped')
    return aarch32_LDRB_r_T2_A_exec


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
                    core.writeR(t, core.Field(data,63,32));
                    core.writeR(t2, core.Field(data,31,0));
                else:
                    core.writeR(t, core.Field(data,31,0));
                    core.writeR(t2, core.Field(data,63,32));
            else:
                core.writeR(t, core.ReadMemA(address,4));
                core.writeR(t2, core.ReadMemA(address+4,4));
            if wback:
                 core.writeR(n, offset_addr);
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
                    core.writeR(t, core.Field(data,31,0));
                    core.writeR(t2, core.Field(data,63,32));
            else:
                core.writeR(t, core.ReadMemA(address,4));
                core.writeR(t2, core.ReadMemA(address+4,4));
        else:
            log.debug(f'aarch32_LDRD_l_T1_A_exec skipped')
    return aarch32_LDRD_l_T1_A_exec


# instruction aarch32_LDREX_A
# pattern LDREX{<c>}{<q>} <Rt>, [<Rn> {, #<imm>}] with bitdiffs=[]
# regex ^LDREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDREX_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) + imm32;
            core.SetExclusiveMonitors(address,4);
            core.writeR(t, core.ReadMemA(address,4));
        else:
            log.debug(f'aarch32_LDREX_T1_A_exec skipped')
    return aarch32_LDREX_T1_A_exec


# instruction aarch32_LDREXB_A
# pattern LDREXB{<c>}{<q>} <Rt>, [<Rn>] with bitdiffs=[]
# regex ^LDREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rt Rn
def aarch32_LDREXB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_LDREXB_T1_A Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREXB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            core.SetExclusiveMonitors(address,1);
            core.writeR(t, core.ZeroExtend(core.ReadMemA(address,1), 32));
        else:
            log.debug(f'aarch32_LDREXB_T1_A_exec skipped')
    return aarch32_LDREXB_T1_A_exec


# instruction aarch32_LDREXH_A
# pattern LDREXH{<c>}{<q>} <Rt>, [<Rn>] with bitdiffs=[]
# regex ^LDREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rt Rn
def aarch32_LDREXH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_LDREXH_T1_A Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREXH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            core.SetExclusiveMonitors(address,2);
            core.writeR(t, core.ZeroExtend(core.ReadMemA(address,2), 32));
        else:
            log.debug(f'aarch32_LDREXH_T1_A_exec skipped')
    return aarch32_LDREXH_T1_A_exec


# instruction aarch32_LDRHT_A
# pattern LDRHT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRHT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRHT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRHT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.readR(m) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            data = MemU_unpriv[address,2];
            if postindex:
                 core.writeR(n, offset_addr);
            core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRHT_T1_A_exec skipped')
    return aarch32_LDRHT_T1_A_exec


# instruction aarch32_LDRH_i_A
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRH_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRH_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_LDRH_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,2);
                if wback:
                     core.writeR(n, offset_addr);
                core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_i_T1_A_exec skipped')
    return aarch32_LDRH_i_T1_A_exec

# pattern LDRH{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRH_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRH_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRH_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,2);
                if wback:
                     core.writeR(n, offset_addr);
                core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_i_T2_A_exec skipped')
    return aarch32_LDRH_i_T2_A_exec

# pattern LDRH{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_LDRH_i_T3_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRH_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if P == '0' and W == '0':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if (t == 15 and W == '1') or (wback and n == t):
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRH_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,2);
                if wback:
                     core.writeR(n, offset_addr);
                core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_i_T3_A_exec skipped')
    return aarch32_LDRH_i_T3_A_exec


# instruction aarch32_LDRH_l_A
# pattern LDRH{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDRH{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt imm32
def aarch32_LDRH_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDRH_l_T1_A Rt={Rt} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = (U == '1');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRH_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            if abs_address is None:
                address = (base + imm32) if add else (base - imm32);
            else:
                address = abs_address;
            data = core.ReadMemU(address,2);
            core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_l_T1_A_exec skipped')
    return aarch32_LDRH_l_T1_A_exec


# instruction aarch32_LDRH_r_A
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_LDRH_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_LDRH_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_LDRH_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.writeR(n, offset_addr);
            core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_r_T1_A_exec skipped')
    return aarch32_LDRH_r_T1_A_exec

# pattern LDRH{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern LDRH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_LDRH_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRH_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRH_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = core.ReadMemU(address,2);
            if wback:
                 core.writeR(n, offset_addr);
            core.writeR(t, core.ZeroExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRH_r_T2_A_exec skipped')
    return aarch32_LDRH_r_T2_A_exec


# instruction aarch32_LDRSBT_A
# pattern LDRSBT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRSBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRSBT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRSBT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSBT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.readR(m) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            core.writeR(t, core.SignExtend(MemU_unpriv[address,1], 32));
            if postindex:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRSBT_T1_A_exec skipped')
    return aarch32_LDRSBT_T1_A_exec


# instruction aarch32_LDRSB_i_A
# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRSB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRSB_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.SignExtend(core.ReadMemU(address,1), 32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRSB_i_T1_A_exec skipped')
    return aarch32_LDRSB_i_T1_A_exec

# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_LDRSB_i_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRSB_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if P == '0' and W == '0':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if (t == 15 and W == '1') or (wback and n == t):
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.SignExtend(core.ReadMemU(address,1), 32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRSB_i_T2_A_exec skipped')
    return aarch32_LDRSB_i_T2_A_exec


# instruction aarch32_LDRSB_l_A
# pattern LDRSB{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDRSB{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt imm32
def aarch32_LDRSB_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDRSB_l_T1_A Rt={Rt} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = (U == '1');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSB_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            if abs_address is None:
                address = (base + imm32) if add else (base - imm32);
            else:
                address = abs_address;
            core.writeR(t, core.SignExtend(core.ReadMemU(address,1), 32));
        else:
            log.debug(f'aarch32_LDRSB_l_T1_A_exec skipped')
    return aarch32_LDRSB_l_T1_A_exec


# instruction aarch32_LDRSB_r_A
# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_LDRSB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_LDRSB_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_LDRSB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.SignExtend(core.ReadMemU(address,1), 32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRSB_r_T1_A_exec skipped')
    return aarch32_LDRSB_r_T1_A_exec

# pattern LDRSB{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern LDRSB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_LDRSB_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDRSB_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRSB_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.writeR(t, core.SignExtend(core.ReadMemU(address,1), 32));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_LDRSB_r_T2_A_exec skipped')
    return aarch32_LDRSB_r_T2_A_exec


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
            offset = core.readR(m) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            data = MemU_unpriv[address,2];
            if postindex:
                 core.writeR(n, offset_addr);
            core.writeR(t, core.SignExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRSHT_T1_A_exec skipped')
    return aarch32_LDRSHT_T1_A_exec


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
                 core.writeR(n, offset_addr);
            core.writeR(t, core.SignExtend(data, 32));
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
                 core.writeR(n, offset_addr);
            core.writeR(t, core.SignExtend(data, 32));
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
            core.writeR(t, core.SignExtend(data, 32));
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
                 core.writeR(n, offset_addr);
            core.writeR(t, core.SignExtend(data, 32));
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
                 core.writeR(n, offset_addr);
            core.writeR(t, core.SignExtend(data, 32));
        else:
            log.debug(f'aarch32_LDRSH_r_T2_A_exec skipped')
    return aarch32_LDRSH_r_T2_A_exec


# instruction aarch32_LDRT_A
# pattern LDRT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDRT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDRT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDRT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDRT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            data = MemU_unpriv[address,4];
            if postindex:
                 core.writeR(n, offset_addr);
            core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDRT_T1_A_exec skipped')
    return aarch32_LDRT_T1_A_exec


# instruction aarch32_LDR_i_A
# pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDR_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDR_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_LDR_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,4);
                if wback:
                     core.writeR(n, offset_addr);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_i_T1_A_exec skipped')
    return aarch32_LDR_i_T1_A_exec

# pattern LDR{<c>}{<q>} <Rt>, [SP{, #{+}<imm>}] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[SP(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt imm32*
def aarch32_LDR_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDR_i_T2_A Rt={Rt} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = 13;  
    index = True;  add = True;  wback = False;

    def aarch32_LDR_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,4);
                if wback:
                     core.writeR(n, offset_addr);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_i_T2_A_exec skipped')
    return aarch32_LDR_i_T2_A_exec

# pattern LDR{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_LDR_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDR_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  index = True;  add = True;
    wback = False;

    def aarch32_LDR_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,4);
                if wback:
                     core.writeR(n, offset_addr);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_i_T3_A_exec skipped')
    return aarch32_LDR_i_T3_A_exec

# pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern LDR{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern LDR{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_LDR_i_T4_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDR_i_T4_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if P == '0' and W == '0':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];
    index = (P == '1');  add = (U == '1');  wback = (W == '1');

    def aarch32_LDR_i_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                data = core.ReadMemU(address,4);
                if wback:
                     core.writeR(n, offset_addr);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_i_T4_A_exec skipped')
    return aarch32_LDR_i_T4_A_exec


# instruction aarch32_LDR_l_A
# pattern LDR{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
def aarch32_LDR_l_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_LDR_l_T1_A Rt={Rt} abs_address={hex(abs_address)} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = True;

    def aarch32_LDR_l_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            address = abs_address;
            data = core.ReadMemU(address,4);
            if t == 15:
                if core.Field(address,1,0) == '00':
                    core.LoadWritePC(data);
                else:
                    raise Exception('UNPREDICTABLE');
            else:
                core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_l_T1_A_exec skipped')
    return aarch32_LDR_l_T1_A_exec

# pattern LDR{<c>}.W <Rt>, <label> with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDR{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rt abs_address
# pattern LDR{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$ : c Rt imm32
def aarch32_LDR_l_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    abs_address = regex_groups.get('abs_address', None)
    if abs_address is not None:
        abs_address = int(abs_address, 16)
    imm32 = regex_groups.get('imm32', None)
    U = bitdiffs.get('U', '1')
    log.debug(f'aarch32_LDR_l_T2_A Rt={Rt} abs_address={hex(abs_address) if abs_address is not None else abs_address} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  add = (U == '1');

    def aarch32_LDR_l_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            base = core.Align(core.PC,4);
            if abs_address is None:
                address = (base + imm32) if add else (base - imm32);
            else:
                address = abs_address;
            data = core.ReadMemU(address,4);
            if t == 15:
                if core.Field(address,1,0) == '00':
                    core.LoadWritePC(data);
                else:
                    raise Exception('UNPREDICTABLE');
            else:
                core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_l_T2_A_exec skipped')
    return aarch32_LDR_l_T2_A_exec


# instruction aarch32_LDR_r_A
# pattern LDR{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_LDR_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_LDR_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_LDR_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
                offset_addr = (core.readR(n) + offset);
                address = offset_addr;
                data = core.ReadMemU(address,4);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_r_T1_A_exec skipped')
    return aarch32_LDR_r_T1_A_exec

# pattern LDR{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern LDR{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_LDR_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_LDR_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_LDR_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
                offset_addr = (core.readR(n) + offset);
                address = offset_addr;
                data = core.ReadMemU(address,4);
                if t == 15:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(data);
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.writeR(t, data);
        else:
            log.debug(f'aarch32_LDR_r_T2_A_exec skipped')
    return aarch32_LDR_r_T2_A_exec


# instruction aarch32_MLA_A
# pattern MLA{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[]
# regex ^MLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_MLA_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    log.debug(f'aarch32_MLA_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  setflags = False;
    if d == 15 or n == 15 or m  == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MLA_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.readR(n)) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.readR(m)) produces the same final results
            addend   = core.SInt(core.R[a]);  # addend   = core.UInt(core.readR(a)) produces the same final results
            result = operand1 * operand2 + addend;
            core.writeR(d, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(core.Field(result,31,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MLA_T1_A_exec skipped')
    return aarch32_MLA_T1_A_exec


# instruction aarch32_MLS_A
# pattern MLS{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[]
# regex ^MLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_MLS_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    log.debug(f'aarch32_MLS_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    if d == 15 or n == 15 or m == 15 or a == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MLS_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.readR(n)) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.readR(m)) produces the same final results
            addend   = core.SInt(core.R[a]);  # addend   = core.UInt(core.readR(a)) produces the same final results
            result = addend - operand1 * operand2;
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_MLS_T1_A_exec skipped')
    return aarch32_MLS_T1_A_exec


# instruction aarch32_MOVT_A
# pattern MOVT{<c>}{<q>} <Rd>, #<imm16> with bitdiffs=[]
# regex ^MOVT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MOVT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_MOVT_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOVT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.SetField(core.readR(d),31,16,imm32));
            # core.Field(core.readR(d),15,0) unchanged
        else:
            log.debug(f'aarch32_MOVT_T1_A_exec skipped')
    return aarch32_MOVT_T1_A_exec


# instruction aarch32_MOV_i_A
# pattern MOV<c>{<q>} <Rd>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVS{<q>} <Rd>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : Rd imm32
def aarch32_MOV_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  carry = core.APSR.C;

    def aarch32_MOV_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T1_A_exec skipped')
    return aarch32_MOV_i_T1_A_exec

# pattern MOV<c>.W <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOV{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVS.W <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : Rd imm32
# pattern MOVS{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MOV_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_i_T2_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T2_A_exec skipped')
    return aarch32_MOV_i_T2_A_exec

# pattern MOV{<c>}{<q>} <Rd>, #<imm16> with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MOVW{<c>}{<q>} <Rd>, #<imm16> with bitdiffs=[]
# regex ^MOVW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MOV_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_MOV_i_T3_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = imm32;
            if d == 15:
                          # Can only occur for encoding A1
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_i_T3_A_exec skipped')
    return aarch32_MOV_i_T3_A_exec


# instruction aarch32_MOV_r_A
# pattern MOV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_MOV_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_MOV_r_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_MOV_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T1_A_exec skipped')
    return aarch32_MOV_r_T1_A_exec

# pattern MOV<c>{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOVS{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : Rd Rm shift_t* shift_n*
# alias   ASRS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   ASR<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSLS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSL<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSRS{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSR<c>{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
def aarch32_MOV_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MOV_r_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');

    def aarch32_MOV_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T2_A_exec skipped')
    return aarch32_MOV_r_T2_A_exec

# pattern MOV{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MOV{<c>}.W <Rd>, <Rm> {, LSL #0} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\sLSL\s#0)?$ : c Rd Rm
# pattern MOV<c>.W <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOV{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MOVS{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MOVS.W <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : Rd Rm shift_t* shift_n*
# pattern MOVS{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# alias   ASRS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   ASRS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ASR<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ASR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSLS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSLS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSL<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSL{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSRS.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t Rd* Rm shift_n
# alias   LSRS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSR<c>.W {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   LSR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   RORS{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   ROR{<c>}{<q>} {<Rd>,} <Rm>, #<imm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$ : shift_t c Rd* Rm shift_n
# alias   RRXS{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>RRX)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : shift_t c Rd* Rm
# alias   RRX{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>RRX)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : shift_t c Rd* Rm
def aarch32_MOV_r_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MOV_r_T3_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_r_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = shifted;
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_r_T3_A_exec skipped')
    return aarch32_MOV_r_T3_A_exec


# instruction aarch32_MOV_rr_A
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111'), ('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111'), ('S', '1')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# alias   ASRS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   ASR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   LSLS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   LSL<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   LSRS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   LSR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# alias   RORS{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# regex ^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t Rdm Rs
# alias   ROR<c>{<q>} {<Rdm>,} <Rdm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rdm Rs
def aarch32_MOV_rr_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    op = bitdiffs.get('op', '0')
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_rr_T1_A Rdm={Rdm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  m = core.reg_num[Rdm];  s = core.reg_num[Rs];
    setflags = (S == '1');  

    def aarch32_MOV_rr_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.readR(s),7,0));
            (result, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T1_A_exec skipped')
    return aarch32_MOV_rr_T1_A_exec

# pattern MOVS.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : Rd Rm shift_t Rs
# pattern MOVS{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV<c>.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# alias   ASRS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   ASRS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ASR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ASR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSLS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   LSLS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSL<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSL{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSRS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   LSRS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   LSR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   RORS.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t Rd* Rm Rs
# alias   RORS{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '1')]
# regex ^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ROR<c>.W {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
# alias   ROR{<c>}{<q>} {<Rd>,} <Rm>, <Rs> with bitdiffs=[('S', '0')]
# regex ^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$ : shift_t c Rd* Rm Rs
def aarch32_MOV_rr_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    cond = regex_groups.get('c', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_rr_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  s = core.reg_num[Rs];
    setflags = (S == '1');  
    if d == 15 or m == 15 or s == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_rr_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.readR(s),7,0));
            (result, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T2_A_exec skipped')
    return aarch32_MOV_rr_T2_A_exec


# instruction aarch32_MRS_AS
# pattern MRS{<c>}{<q>} <Rd>, <spec_reg> with bitdiffs=[]
# regex ^MRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<spec_reg>\w+)$ : c Rd spec_reg
def aarch32_MRS_T1_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    spec_reg = regex_groups.get('spec_reg', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_MRS_T1_AS Rd={Rd} spec_reg={spec_reg} cond={cond}')
    # decode
    d = core.reg_num[Rd];  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MRS_T1_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.ReadSpecReg(spec_reg));
        else:
            log.debug(f'aarch32_MRS_T1_AS_exec skipped')
    return aarch32_MRS_T1_AS_exec


# instruction aarch32_MRS_br_AS

# instruction aarch32_MSR_br_AS

# instruction aarch32_MSR_r_AS
# pattern MSR{<c>}{<q>} <spec_reg>, <Rn> with bitdiffs=[]
# regex ^MSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<spec_reg>\w+),\s(?P<Rn>\w+)$ : c spec_reg Rn
def aarch32_MSR_r_T1_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    spec_reg = regex_groups.get('spec_reg', None)
    Rn = regex_groups.get('Rn', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_MSR_r_T1_AS spec_reg={spec_reg} Rn={Rn} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MSR_r_T1_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            core.WriteSpecReg(spec_reg, core.readR(n));
        else:
            log.debug(f'aarch32_MSR_r_T1_AS_exec skipped')
    return aarch32_MSR_r_T1_AS_exec


# instruction aarch32_MUL_A
# pattern MUL<c>{<q>} <Rdm>, <Rn>{, <Rdm>} with bitdiffs=[('S', '0')]
# regex ^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$ : c Rdm Rn
# pattern MULS{<q>} <Rdm>, <Rn>{, <Rdm>} with bitdiffs=[('S', '1')]
# regex ^MULS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$ : Rdm Rn
def aarch32_MUL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    Rn = regex_groups.get('Rn', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MUL_T1_A Rdm={Rdm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  n = core.reg_num[Rn];  m = core.reg_num[Rdm];  setflags = (S == '1');

    def aarch32_MUL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.readR(n)) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.readR(m)) produces the same final results
            result = operand1 * operand2;
            core.writeR(d, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(core.Field(result,31,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MUL_T1_A_exec skipped')
    return aarch32_MUL_T1_A_exec

# pattern MUL<c>.W <Rd>, <Rn>{, <Rm>} with bitdiffs=[]
# regex ^MUL(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$ : c Rd Rn Rm*
# pattern MUL{<c>}{<q>} <Rd>, <Rn>{, <Rm>} with bitdiffs=[]
# regex ^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$ : c Rd Rn Rm*
def aarch32_MUL_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rm is None:
        Rm = Rd
    log.debug(f'aarch32_MUL_T2_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = False;
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MUL_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.readR(n)) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.readR(m)) produces the same final results
            result = operand1 * operand2;
            core.writeR(d, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(core.Field(result,31,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MUL_T2_A_exec skipped')
    return aarch32_MUL_T2_A_exec


# instruction aarch32_MVN_i_A
# pattern MVN{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '0')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
# pattern MVNS{<c>}{<q>} <Rd>, #<const> with bitdiffs=[('S', '1')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$ : c Rd imm32
def aarch32_MVN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MVN_i_T1_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MVN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.NOT(imm32);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MVN_i_T1_A_exec skipped')
    return aarch32_MVN_i_T1_A_exec


# instruction aarch32_MVN_r_A
# pattern MVN<c>{<q>} <Rd>, <Rm> with bitdiffs=[('S', '0')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern MVNS{<q>} <Rd>, <Rm> with bitdiffs=[('S', '1')]
# regex ^MVNS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : Rd Rm
def aarch32_MVN_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MVN_r_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_MVN_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MVN_r_T1_A_exec skipped')
    return aarch32_MVN_r_T1_A_exec

# pattern MVN{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MVN<c>.W <Rd>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern MVN{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
# pattern MVNS{<c>}{<q>} <Rd>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd Rm shift_t
# pattern MVNS.W <Rd>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : Rd Rm
# pattern MVNS{<c>}{<q>} <Rd>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd Rm shift_t* shift_n*
def aarch32_MVN_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_MVN_r_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MVN_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.NOT(shifted);
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MVN_r_T2_A_exec skipped')
    return aarch32_MVN_r_T2_A_exec


# instruction aarch32_NOP_A
# pattern NOP{<c>}{<q>} with bitdiffs=[]
# regex ^NOP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$ : c
def aarch32_NOP_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_NOP_T1_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_NOP_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            pass # Do nothing
        else:
            log.debug(f'aarch32_NOP_T1_A_exec skipped')
    return aarch32_NOP_T1_A_exec

# pattern NOP{<c>}.W with bitdiffs=[]
# regex ^NOP(?P<c>[ACEGHLMNPV][CEILQST])?.W$ : c
def aarch32_NOP_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    log.debug(f'aarch32_NOP_T2_A cond={cond}')
    # decode
    # No additional decoding required

    def aarch32_NOP_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            pass # Do nothing
        else:
            log.debug(f'aarch32_NOP_T2_A_exec skipped')
    return aarch32_NOP_T2_A_exec


# instruction aarch32_ORN_i_A
# pattern ORNS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ORN{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ORN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ORN_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ORN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) | core.NOT(imm32);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORN_i_T1_A_exec skipped')
    return aarch32_ORN_i_T1_A_exec


# instruction aarch32_ORN_r_A
# pattern ORN{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ORN{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern ORNS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ORNS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_ORN_r_T1_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_ORN_r_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ORN_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) | core.NOT(shifted);
            core.writeR(d, core.Field(result));
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORN_r_T1_A_exec skipped')
    return aarch32_ORN_r_T1_A_exec


# instruction aarch32_ORR_i_A
# pattern ORR{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ORRS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ORR_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ORR_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ORR_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) | imm32;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORR_i_T1_A_exec skipped')
    return aarch32_ORR_i_T1_A_exec


# instruction aarch32_ORR_r_A
# pattern ORR<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern ORRS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^ORRS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^ORRS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_ORR_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_ORR_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_ORR_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) | shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORR_r_T1_A_exec skipped')
    return aarch32_ORR_r_T1_A_exec

# pattern ORR{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ORR<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern ORR{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern ORRS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern ORRS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ORRS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern ORRS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_ORR_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_ORR_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ORR_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) | shifted;
            if d == 15:
                          # Can only occur for A32 encoding
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.N = core.Bit(result,31);
                    core.APSR.Z = core.IsZeroBit(result);
                    core.APSR.C = carry;
                    # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORR_r_T2_A_exec skipped')
    return aarch32_ORR_r_T2_A_exec


# instruction aarch32_PKH_A
# pattern PKHBT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, LSL #<imm>} with bitdiffs=[('tb', '0')]
# regex ^PKHBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern PKHTB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ASR #<imm>} with bitdiffs=[('tb', '1')]
# regex ^PKHTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_PKH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    tb = bitdiffs.get('tb', '0')
    S = bitdiffs.get('S', '0')
    T = bitdiffs.get('T', '0')
    if Rd is None:
        Rd = Rn
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_PKH_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    if S == '1' or T == '1':
        raise Exception('UNDEFINED');
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  tbform = (tb == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_PKH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);  # core.APSR.C ignored
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(operand2,15,0) if tbform else core.Field(core.readR(n),15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(core.readR(n),31,16)    if tbform else core.Field(operand2,31,16)));
        else:
            log.debug(f'aarch32_PKH_T1_A_exec skipped')
    return aarch32_PKH_T1_A_exec


# instruction aarch32_POP_A
# pattern POP{<c>}{<q>} <registers> with bitdiffs=[]
# regex ^POP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$ : c registers
# pattern LDM{<c>}{<q>} SP!, <registers> with bitdiffs=[]
# regex ^LDM(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$ : c registers
def aarch32_POP_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_POP_T1_A cond={cond} reg_list={reg_list}')
    # decode
    UnalignedAllowed = False;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_POP_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(13);
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.writeR(i, core.ReadMemU(address,4) if UnalignedAllowed else core.ReadMemA(address,4));
                    address = address + 4;
            if registers[15] == '1':
                if UnalignedAllowed:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(core.ReadMemU(address,4));
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.LoadWritePC(core.ReadMemA(address,4));
            if registers[13] == '0':
                 core.writeR(13, core.readR(13) + 4*registers.count('1'));
            if registers[13] == '1':
                 core.writeR(13, UNKNOWN = 0);
        else:
            log.debug(f'aarch32_POP_T1_A_exec skipped')
    return aarch32_POP_T1_A_exec


# instruction aarch32_PUSH_A
# pattern PUSH{<c>}{<q>} <registers> with bitdiffs=[]
# regex ^PUSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$ : c registers
# pattern STMDB{<c>}{<q>} SP!, <registers> with bitdiffs=[]
# regex ^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$ : c registers
def aarch32_PUSH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_PUSH_T1_A cond={cond} reg_list={reg_list}')
    # decode
    UnalignedAllowed = False;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_PUSH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(13) - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == 13 and i != core.LowestSetBit(registers):  # Only possible for encoding A1
                        core.WriteMemA(address,4, UNKNOWN = 0);
                    else:
                        if UnalignedAllowed:
                            core.WriteMemU(address,4, core.readR(i));
                        else:
                            core.WriteMemA(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1 or A2
                if UnalignedAllowed:
                    core.WriteMemU(address,4, core.PCStoreValue());
                else:
                    core.WriteMemA(address,4, core.PCStoreValue());
            core.writeR(13, core.readR(13) - 4*registers.count('1'));
        else:
            log.debug(f'aarch32_PUSH_T1_A_exec skipped')
    return aarch32_PUSH_T1_A_exec


# instruction aarch32_QADD_A
# pattern QADD{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QADD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QADD_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QADD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sat = False;
            (core.R[d], sat) = core.SignedSatQ(core.SInt(core.readR(m)) + core.SInt(core.readR(n)), 32);
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QADD_T1_A_exec skipped')
    return aarch32_QADD_T1_A_exec


# instruction aarch32_QADD16_A
# pattern QADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),15,0));
            sum2 = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignedSat(sum1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignedSat(sum2, 16)));
        else:
            log.debug(f'aarch32_QADD16_T1_A_exec skipped')
    return aarch32_QADD16_T1_A_exec


# instruction aarch32_QADD8_A
# pattern QADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),7,0)) + core.SInt(core.Field(core.readR(m),7,0));
            sum2 = core.SInt(core.Field(core.readR(n),15,8)) + core.SInt(core.Field(core.readR(m),15,8));
            sum3 = core.SInt(core.Field(core.readR(n),23,16)) + core.SInt(core.Field(core.readR(m),23,16));
            sum4 = core.SInt(core.Field(core.readR(n),31,24)) + core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.SignedSat(sum1, 8)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.SignedSat(sum2, 8)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.SignedSat(sum3, 8)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.SignedSat(sum4, 8)));
        else:
            log.debug(f'aarch32_QADD8_T1_A_exec skipped')
    return aarch32_QADD8_T1_A_exec


# instruction aarch32_QASX_A
# pattern QASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),31,16));
            sum  = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignedSat(diff, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignedSat(sum, 16)));
        else:
            log.debug(f'aarch32_QASX_T1_A_exec skipped')
    return aarch32_QASX_T1_A_exec


# instruction aarch32_QDADD_A
# pattern QDADD{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QDADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QDADD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QDADD_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QDADD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (doubled, sat1) = core.SignedSatQ(2 * core.SInt(core.readR(n)), 32);
            sat2 = False;
            (core.R[d], sat2)  = core.SignedSatQ(core.SInt(core.readR(m)) + core.SInt(doubled), 32);
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QDADD_T1_A_exec skipped')
    return aarch32_QDADD_T1_A_exec


# instruction aarch32_QDSUB_A
# pattern QDSUB{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QDSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QDSUB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QDSUB_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QDSUB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (doubled, sat1) = core.SignedSatQ(2 * core.SInt(core.readR(n)), 32);
            sat2 = False;
            (core.R[d], sat2)  = core.SignedSatQ(core.SInt(core.readR(m)) - core.SInt(doubled), 32);
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QDSUB_T1_A_exec skipped')
    return aarch32_QDSUB_T1_A_exec


# instruction aarch32_QSAX_A
# pattern QSAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QSAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),31,16));
            diff = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignedSat(sum, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignedSat(diff, 16)));
        else:
            log.debug(f'aarch32_QSAX_T1_A_exec skipped')
    return aarch32_QSAX_T1_A_exec


# instruction aarch32_QSUB_A
# pattern QSUB{<c>}{<q>} {<Rd>,} <Rm>, <Rn> with bitdiffs=[]
# regex ^QSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$ : c Rd* Rm Rn
def aarch32_QSUB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = regex_groups.get('Rn', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSUB_T1_A Rd={Rd} Rm={Rm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSUB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sat = False;
            (core.R[d], sat) = core.SignedSatQ(core.SInt(core.readR(m)) - core.SInt(core.readR(n)), 32);
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_QSUB_T1_A_exec skipped')
    return aarch32_QSUB_T1_A_exec


# instruction aarch32_QSUB16_A
# pattern QSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),15,0));
            diff2 = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignedSat(diff1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignedSat(diff2, 16)));
        else:
            log.debug(f'aarch32_QSUB16_T1_A_exec skipped')
    return aarch32_QSUB16_T1_A_exec


# instruction aarch32_QSUB8_A
# pattern QSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^QSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_QSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_QSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_QSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),7,0)) - core.SInt(core.Field(core.readR(m),7,0));
            diff2 = core.SInt(core.Field(core.readR(n),15,8)) - core.SInt(core.Field(core.readR(m),15,8));
            diff3 = core.SInt(core.Field(core.readR(n),23,16)) - core.SInt(core.Field(core.readR(m),23,16));
            diff4 = core.SInt(core.Field(core.readR(n),31,24)) - core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.SignedSat(diff1, 8)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.SignedSat(diff2, 8)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.SignedSat(diff3, 8)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.SignedSat(diff4, 8)));
        else:
            log.debug(f'aarch32_QSUB8_T1_A_exec skipped')
    return aarch32_QSUB8_T1_A_exec


# instruction aarch32_RBIT_A
# pattern RBIT{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^RBIT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_RBIT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    Rn = Rm
    log.debug(f'aarch32_RBIT_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_RBIT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.Field(int(f'{core.UInt(core.readR(m)):032b}'[::-1],2)))
        else:
            log.debug(f'aarch32_RBIT_T1_A_exec skipped')
    return aarch32_RBIT_T1_A_exec


# instruction aarch32_REV_A
# pattern REV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];

    def aarch32_REV_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),7,0));
            result = core.SetField(result,23,16,core.Field(core.readR(m),15,8));
            result = core.SetField(result,15,8,core.Field(core.readR(m),23,16));
            result = core.SetField(result,7,0,core.Field(core.readR(m),31,24));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV_T1_A_exec skipped')
    return aarch32_REV_T1_A_exec

# pattern REV{<c>}.W <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern REV{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV_T2_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_REV_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),7,0));
            result = core.SetField(result,23,16,core.Field(core.readR(m),15,8));
            result = core.SetField(result,15,8,core.Field(core.readR(m),23,16));
            result = core.SetField(result,7,0,core.Field(core.readR(m),31,24));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV_T2_A_exec skipped')
    return aarch32_REV_T2_A_exec


# instruction aarch32_REV16_A
# pattern REV16{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV16_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];

    def aarch32_REV16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),23,16));
            result = core.SetField(result,23,16,core.Field(core.readR(m),31,24));
            result = core.SetField(result,15,8,core.Field(core.readR(m),7,0));
            result = core.SetField(result,7,0,core.Field(core.readR(m),15,8));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV16_T1_A_exec skipped')
    return aarch32_REV16_T1_A_exec

# pattern REV16{<c>}.W <Rd>, <Rm> with bitdiffs=[]
# regex ^REV16(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern REV16{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REV16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REV16_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REV16_T2_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_REV16_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,24,core.Field(core.readR(m),23,16));
            result = core.SetField(result,23,16,core.Field(core.readR(m),31,24));
            result = core.SetField(result,15,8,core.Field(core.readR(m),7,0));
            result = core.SetField(result,7,0,core.Field(core.readR(m),15,8));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REV16_T2_A_exec skipped')
    return aarch32_REV16_T2_A_exec


# instruction aarch32_REVSH_A
# pattern REVSH{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REVSH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REVSH_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];

    def aarch32_REVSH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,8,core.SignExtend(core.Field(core.readR(m),7,0), 24));
            result = core.SetField(result,7,0,core.Field(core.readR(m),15,8));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REVSH_T1_A_exec skipped')
    return aarch32_REVSH_T1_A_exec

# pattern REVSH{<c>}.W <Rd>, <Rm> with bitdiffs=[]
# regex ^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
# pattern REVSH{<c>}{<q>} <Rd>, <Rm> with bitdiffs=[]
# regex ^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$ : c Rd Rm
def aarch32_REVSH_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_REVSH_T2_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  n = core.reg_num[Rn];
    if m != n or d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_REVSH_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            result = core.SetField(result,31,8,core.SignExtend(core.Field(core.readR(m),7,0), 24));
            result = core.SetField(result,7,0,core.Field(core.readR(m),15,8));
            core.writeR(d, core.Field(result));
        else:
            log.debug(f'aarch32_REVSH_T2_A_exec skipped')
    return aarch32_REVSH_T2_A_exec


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


# instruction aarch32_SADD16_A
# pattern SADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),15,0));
            sum2 = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum1,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum2,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if sum1 >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum2 >= 0 else '00');
        else:
            log.debug(f'aarch32_SADD16_T1_A_exec skipped')
    return aarch32_SADD16_T1_A_exec


# instruction aarch32_SADD8_A
# pattern SADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),7,0)) + core.SInt(core.Field(core.readR(m),7,0));
            sum2 = core.SInt(core.Field(core.readR(n),15,8)) + core.SInt(core.Field(core.readR(m),15,8));
            sum3 = core.SInt(core.Field(core.readR(n),23,16)) + core.SInt(core.Field(core.readR(m),23,16));
            sum4 = core.SInt(core.Field(core.readR(n),31,24)) + core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,7,0)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,7,0)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,7,0)));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if sum1 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if sum2 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if sum3 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if sum4 >= 0 else '0')
        else:
            log.debug(f'aarch32_SADD8_T1_A_exec skipped')
    return aarch32_SADD8_T1_A_exec


# instruction aarch32_SASX_A
# pattern SASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),31,16));
            sum  = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum  >= 0 else '00');
        else:
            log.debug(f'aarch32_SASX_T1_A_exec skipped')
    return aarch32_SASX_T1_A_exec


# instruction aarch32_SBC_i_A
# pattern SBC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern SBCS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_SBC_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SBC_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SBC_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), core.APSR.C);
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
            log.debug(f'aarch32_SBC_i_T1_A_exec skipped')
    return aarch32_SBC_i_T1_A_exec


# instruction aarch32_SBC_r_A
# pattern SBC<c>{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : c Rdn Rm
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : c Rdn Rm
# pattern SBCS{<q>} {<Rdn>,} <Rdn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^SBCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$ : Rdn Rm
# regex ^SBCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$ : Rdn Rm
def aarch32_SBC_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_SBC_r_T1_A Rdn={Rdn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_SBC_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), core.APSR.C);
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
            log.debug(f'aarch32_SBC_r_T1_A_exec skipped')
    return aarch32_SBC_r_T1_A_exec

# pattern SBC{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern SBC<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SBC{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern SBCS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern SBCS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SBCS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern SBCS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_SBC_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_SBC_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SBC_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), core.APSR.C);
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
            log.debug(f'aarch32_SBC_r_T2_A_exec skipped')
    return aarch32_SBC_r_T2_A_exec


# instruction aarch32_SBFX_A
# pattern SBFX{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^SBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_SBFX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_SBFX_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];
    lsbit = core.UInt(lsb);  
    msbit = core.UInt(width) - 1 + core.UInt(lsb);
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit > 31:
        msbit = 31;

    def aarch32_SBFX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.SignExtendSubField(core.readR(n), msbit, lsbit, 32));
        else:
            log.debug(f'aarch32_SBFX_T1_A_exec skipped')
    return aarch32_SBFX_T1_A_exec


# instruction aarch32_SDIV_A
# pattern SDIV{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SDIV_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SDIV_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = 15;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == 15 or n == 15 or m == 15 or a != 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_SDIV_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            if core.SInt(core.R[m]) == 0:
                result = 0;
            else:
                result = core.RoundTowardsZero(core.Real(core.SInt(core.readR(n))) / core.Real(core.SInt(core.readR(m))));
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_SDIV_T1_A_exec skipped')
    return aarch32_SDIV_T1_A_exec


# instruction aarch32_SEL_A
# pattern SEL{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SEL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SEL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SEL_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SEL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(core.readR(n),7,0)   if core.APSR.GE[0] else core.Field(core.readR(m),7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(core.readR(n),15,8)  if core.APSR.GE[1] else core.Field(core.readR(m),15,8)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(core.readR(n),23,16) if core.APSR.GE[2] else core.Field(core.readR(m),23,16)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(core.readR(n),31,24) if core.APSR.GE[3] else core.Field(core.readR(m),31,24)));
        else:
            log.debug(f'aarch32_SEL_T1_A_exec skipped')
    return aarch32_SEL_T1_A_exec


# instruction aarch32_SHADD16_A
# pattern SHADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),15,0));
            sum2 = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum1,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum2,16,1)));
        else:
            log.debug(f'aarch32_SHADD16_T1_A_exec skipped')
    return aarch32_SHADD16_T1_A_exec


# instruction aarch32_SHADD8_A
# pattern SHADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.SInt(core.Field(core.readR(n),7,0)) + core.SInt(core.Field(core.readR(m),7,0));
            sum2 = core.SInt(core.Field(core.readR(n),15,8)) + core.SInt(core.Field(core.readR(m),15,8));
            sum3 = core.SInt(core.Field(core.readR(n),23,16)) + core.SInt(core.Field(core.readR(m),23,16));
            sum4 = core.SInt(core.Field(core.readR(n),31,24)) + core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,8,1)));
        else:
            log.debug(f'aarch32_SHADD8_T1_A_exec skipped')
    return aarch32_SHADD8_T1_A_exec


# instruction aarch32_SHASX_A
# pattern SHASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),31,16));
            sum  = core.SInt(core.Field(core.readR(n),31,16)) + core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum,16,1)));
        else:
            log.debug(f'aarch32_SHASX_T1_A_exec skipped')
    return aarch32_SHASX_T1_A_exec


# instruction aarch32_SHSAX_A
# pattern SHSAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHSAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHSAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHSAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),31,16));
            diff = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff,16,1)));
        else:
            log.debug(f'aarch32_SHSAX_T1_A_exec skipped')
    return aarch32_SHSAX_T1_A_exec


# instruction aarch32_SHSUB16_A
# pattern SHSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),15,0));
            diff2 = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff1,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff2,16,1)));
        else:
            log.debug(f'aarch32_SHSUB16_T1_A_exec skipped')
    return aarch32_SHSUB16_T1_A_exec


# instruction aarch32_SHSUB8_A
# pattern SHSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SHSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SHSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SHSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),7,0)) - core.SInt(core.Field(core.readR(m),7,0));
            diff2 = core.SInt(core.Field(core.readR(n),15,8)) - core.SInt(core.Field(core.readR(m),15,8));
            diff3 = core.SInt(core.Field(core.readR(n),23,16)) - core.SInt(core.Field(core.readR(m),23,16));
            diff4 = core.SInt(core.Field(core.readR(n),31,24)) - core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(diff1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(diff2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(diff3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(diff4,8,1)));
        else:
            log.debug(f'aarch32_SHSUB8_T1_A_exec skipped')
    return aarch32_SHSUB8_T1_A_exec


# instruction aarch32_SMLABB_A
# pattern SMLABB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMLABB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLABT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMLABT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLATB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMLATB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLATT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMLATT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLABB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLABB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    n_high = (N == '1');  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLABB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.readR(n),31,16) if n_high else core.Field(core.readR(n),15,0);
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(operand1) * core.SInt(operand2) + core.SInt(core.readR(a));
            core.writeR(d, core.Field(result,31,0));
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLABB_T1_A_exec skipped')
    return aarch32_SMLABB_T1_A_exec


# instruction aarch32_SMLAD_A
# pattern SMLAD{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '0')]
# regex ^SMLAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLADX{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '1')]
# regex ^SMLADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLAD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLAD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLAD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 + product2 + core.SInt(core.readR(a));
            core.writeR(d, core.Field(result,31,0));
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLAD_T1_A_exec skipped')
    return aarch32_SMLAD_T1_A_exec


# instruction aarch32_SMLAL_A
# pattern SMLAL{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[]
# regex ^SMLAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLAL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_SMLAL_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = False;
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLAL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.SInt(core.readR(n)) * core.SInt(core.readR(m)) + core.SInt(core.readR(dLo), core.readR(dHi));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,63);
                core.APSR.Z = core.IsZeroBit(core.Field(result,63,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_SMLAL_T1_A_exec skipped')
    return aarch32_SMLAL_T1_A_exec


# instruction aarch32_SMLALBB_A
# pattern SMLALBB{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMLALBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALBT{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMLALBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALTB{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMLALTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALTT{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMLALTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLALBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLALBB_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    n_high = (N == '1');  m_high = (M == '1');
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLALBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.readR(n),31,16) if n_high else core.Field(core.readR(n),15,0);
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(operand1) * core.SInt(operand2) + core.SInt(core.readR(dLo), core.readR(dHi));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_SMLALBB_T1_A_exec skipped')
    return aarch32_SMLALBB_T1_A_exec


# instruction aarch32_SMLALD_A
# pattern SMLALD{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMLALD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLALDX{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMLALDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLALD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLALD_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLALD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 + product2 + core.SInt(core.readR(dLo), core.readR(dHi));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_SMLALD_T1_A_exec skipped')
    return aarch32_SMLALD_T1_A_exec


# instruction aarch32_SMLAWB_A
# pattern SMLAWB{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '0')]
# regex ^SMLAWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLAWT{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '1')]
# regex ^SMLAWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLAWB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLAWB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLAWB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(core.readR(n)) * core.SInt(operand2) + (core.SInt(core.readR(a)) << 16);
            core.writeR(d, core.Field(result,47,16));
            if (result >> 16) != core.SInt(core.readR(d)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLAWB_T1_A_exec skipped')
    return aarch32_SMLAWB_T1_A_exec


# instruction aarch32_SMLSD_A
# pattern SMLSD{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '0')]
# regex ^SMLSD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMLSDX{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('M', '1')]
# regex ^SMLSDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMLSD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLSD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMLSD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = (product1 - product2) + core.SInt(core.readR(a));
            core.writeR(d, core.Field(result,31,0));
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMLSD_T1_A_exec skipped')
    return aarch32_SMLSD_T1_A_exec


# instruction aarch32_SMLSLD_A
# pattern SMLSLD{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMLSLD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
# pattern SMLSLDX{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMLSLDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMLSLD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_SMLSLD_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes UPREDICTABLE for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMLSLD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = (product1 - product2) + core.SInt(core.readR(dLo), core.readR(dHi));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_SMLSLD_T1_A_exec skipped')
    return aarch32_SMLSLD_T1_A_exec


# instruction aarch32_SMMLA_A
# pattern SMMLA{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '0')]
# regex ^SMMLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMMLAR{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '1')]
# regex ^SMMLAR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMMLA_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_SMMLA_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  round = (R == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMLA_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.SInt(core.readR(a)) << 32) + core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            if round:
                 result = result + 0x80000000;
            core.writeR(d, core.Field(result,63,32));
        else:
            log.debug(f'aarch32_SMMLA_T1_A_exec skipped')
    return aarch32_SMMLA_T1_A_exec


# instruction aarch32_SMMLS_A
# pattern SMMLS{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '0')]
# regex ^SMMLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
# pattern SMMLSR{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[('R', '1')]
# regex ^SMMLSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_SMMLS_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_SMMLS_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];  round = (R == '1');
    if d == 15 or n == 15 or m == 15 or a == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMLS_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.SInt(core.readR(a)) << 32) - core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            if round:
                 result = result + 0x80000000;
            core.writeR(d, core.Field(result,63,32));
        else:
            log.debug(f'aarch32_SMMLS_T1_A_exec skipped')
    return aarch32_SMMLS_T1_A_exec


# instruction aarch32_SMMUL_A
# pattern SMMUL{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('R', '0')]
# regex ^SMMUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMMULR{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('R', '1')]
# regex ^SMMULR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMMUL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    R = bitdiffs.get('R', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMMUL_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  round = (R == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMMUL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            if round:
                 result = result + 0x80000000;
            core.writeR(d, core.Field(result,63,32));
        else:
            log.debug(f'aarch32_SMMUL_T1_A_exec skipped')
    return aarch32_SMMUL_T1_A_exec


# instruction aarch32_SMUAD_A
# pattern SMUAD{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMUAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMUADX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMUADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMUAD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMUAD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMUAD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 + product2;
            core.writeR(d, core.Field(result,31,0));
            if result != core.SInt(core.Field(result,31,0)):
                  # Signed overflow
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SMUAD_T1_A_exec skipped')
    return aarch32_SMUAD_T1_A_exec


# instruction aarch32_SMULBB_A
# pattern SMULBB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '0')]
# regex ^SMULBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULBT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '0'), ('M', '1')]
# regex ^SMULBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULTB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '0')]
# regex ^SMULTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULTT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('N', '1'), ('M', '1')]
# regex ^SMULTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMULBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    N = bitdiffs.get('N', '0')
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMULBB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    n_high = (N == '1');  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMULBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.Field(core.readR(n),31,16) if n_high else core.Field(core.readR(n),15,0);
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            result = core.SInt(operand1) * core.SInt(operand2);
            core.writeR(d, core.Field(result,31,0));
            # Signed overflow cannot occur
        else:
            log.debug(f'aarch32_SMULBB_T1_A_exec skipped')
    return aarch32_SMULBB_T1_A_exec


# instruction aarch32_SMULL_A
# pattern SMULL{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[]
# regex ^SMULL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_SMULL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_SMULL_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = False;
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_SMULL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.SInt(core.readR(n)) * core.SInt(core.readR(m));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,63);
                core.APSR.Z = core.IsZeroBit(core.Field(result,63,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_SMULL_T1_A_exec skipped')
    return aarch32_SMULL_T1_A_exec


# instruction aarch32_SMULWB_A
# pattern SMULWB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMULWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMULWT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMULWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMULWB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMULWB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_high = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMULWB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Field(core.readR(m),31,16) if m_high else core.Field(core.readR(m),15,0);
            product = core.SInt(core.readR(n)) * core.SInt(operand2);
            core.writeR(d, core.Field(product,47,16));
            # Signed overflow cannot occur
        else:
            log.debug(f'aarch32_SMULWB_T1_A_exec skipped')
    return aarch32_SMULWB_T1_A_exec


# instruction aarch32_SMUSD_A
# pattern SMUSD{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '0')]
# regex ^SMUSD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SMUSDX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('M', '1')]
# regex ^SMUSDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SMUSD_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    M = bitdiffs.get('M', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SMUSD_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  m_swap = (M == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SMUSD_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.ROR(core.readR(m),16) if m_swap else core.readR(m);
            product1 = core.SInt(core.Field(core.readR(n),15,0)) * core.SInt(core.Field(operand2,15,0));
            product2 = core.SInt(core.Field(core.readR(n),31,16)) * core.SInt(core.Field(operand2,31,16));
            result = product1 - product2;
            core.writeR(d, core.Field(result,31,0));
            # Signed overflow cannot occur
        else:
            log.debug(f'aarch32_SMUSD_T1_A_exec skipped')
    return aarch32_SMUSD_T1_A_exec


# instruction aarch32_SSAT_A
# pattern SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, ASR #<amount> with bitdiffs=[('sh', '1')]
# regex ^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$ : c Rd imm32 Rn shift_t shift_n
# pattern SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn> {, LSL #<amount>} with bitdiffs=[('sh', '0')]
# regex ^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$ : c Rd imm32 Rn shift_t* shift_n*
def aarch32_SSAT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    sh = bitdiffs.get('sh', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SSAT_T1_A Rd={Rd} imm32={imm32} Rn={Rn} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSAT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand = core.Shift(core.readR(n), shift_t, shift_n, core.APSR.C);  # core.APSR.C ignored
            (result, sat) = core.SignedSatQ(core.SInt(operand), imm32);
            core.writeR(d, core.SignExtend(result, 32));
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SSAT_T1_A_exec skipped')
    return aarch32_SSAT_T1_A_exec


# instruction aarch32_SSAT16_A
# pattern SSAT16{<c>}{<q>} <Rd>, #<imm>, <Rn> with bitdiffs=[]
# regex ^SSAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$ : c Rd imm32 Rn
def aarch32_SSAT16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_SSAT16_T1_A Rd={Rd} imm32={imm32} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSAT16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result1, sat1) = core.SignedSatQ(core.SInt(core.Field(core.readR(n),15,0)), imm32);
            (result2, sat2) = core.SignedSatQ(core.SInt(core.Field(core.readR(n),31,16)), imm32);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignExtend(result1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignExtend(result2, 16)));
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SSAT16_T1_A_exec skipped')
    return aarch32_SSAT16_T1_A_exec


# instruction aarch32_SSAX_A
# pattern SSAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SSAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SSAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.SInt(core.Field(core.readR(n),15,0)) + core.SInt(core.Field(core.readR(m),31,16));
            diff = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if sum  >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if diff >= 0 else '00');
        else:
            log.debug(f'aarch32_SSAX_T1_A_exec skipped')
    return aarch32_SSAX_T1_A_exec


# instruction aarch32_SSUB16_A
# pattern SSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),15,0)) - core.SInt(core.Field(core.readR(m),15,0));
            diff2 = core.SInt(core.Field(core.readR(n),31,16)) - core.SInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff1,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff2,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff1 >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if diff2 >= 0 else '00');
        else:
            log.debug(f'aarch32_SSUB16_T1_A_exec skipped')
    return aarch32_SSUB16_T1_A_exec


# instruction aarch32_SSUB8_A
# pattern SSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_SSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.SInt(core.Field(core.readR(n),7,0)) - core.SInt(core.Field(core.readR(m),7,0));
            diff2 = core.SInt(core.Field(core.readR(n),15,8)) - core.SInt(core.Field(core.readR(m),15,8));
            diff3 = core.SInt(core.Field(core.readR(n),23,16)) - core.SInt(core.Field(core.readR(m),23,16));
            diff4 = core.SInt(core.Field(core.readR(n),31,24)) - core.SInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(diff1,7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(diff2,7,0)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(diff3,7,0)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(diff4,7,0)));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if diff1 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if diff2 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if diff3 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if diff4 >= 0 else '0')
        else:
            log.debug(f'aarch32_SSUB8_T1_A_exec skipped')
    return aarch32_SSUB8_T1_A_exec


# instruction aarch32_STM_A
# pattern STM{IA}{<c>}{<q>} <Rn>!, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# pattern STMEA{<c>}{<q>} <Rn>!, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
def aarch32_STM_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_STM_T1_A Rn={Rn} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  wback = True;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_STM_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encodings T1 and A1
                    else:
                        core.WriteMemS(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
        else:
            log.debug(f'aarch32_STM_T1_A_exec skipped')
    return aarch32_STM_T1_A_exec

# pattern STM{IA}{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STMEA{<c>}.W <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STM{IA}{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STMEA{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_STM_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    W = bitdiffs.get('W', '0')
    log.debug(f'aarch32_STM_T2_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15 or registers.count('1') < 2:
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[15] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_STM_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encodings T1 and A1
                    else:
                        core.WriteMemS(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.writeR(n, core.readR(n) + 4*registers.count('1'));
        else:
            log.debug(f'aarch32_STM_T2_A_exec skipped')
    return aarch32_STM_T2_A_exec


# instruction aarch32_STMDB_A
# pattern STMDB{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
# pattern STMFD{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# regex ^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$ : c Rn wback registers
def aarch32_STMDB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    wback = regex_groups.get('wback', None) is not None
    W = bitdiffs.get('W', '0')
    log.debug(f'aarch32_STMDB_T1_A Rn={Rn} wback={wback} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15 or registers.count('1') < 2:
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[15] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_STMDB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encoding A1
                    else:
                        core.WriteMemS(address,4, core.readR(i));
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.writeR(n, core.readR(n) - 4*registers.count('1'));
        else:
            log.debug(f'aarch32_STMDB_T1_A_exec skipped')
    return aarch32_STMDB_T1_A_exec


# instruction aarch32_STRBT_A
# pattern STRBT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRBT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRBT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRBT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            MemU_unpriv[address,1] = core.Field(core.readR(t),7,0);
            if postindex:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRBT_T1_A_exec skipped')
    return aarch32_STRBT_T1_A_exec


# instruction aarch32_STRB_i_A
# pattern STRB{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRB_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_STRB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,1, core.Field(core.readR(t),7,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRB_i_T1_A_exec skipped')
    return aarch32_STRB_i_T1_A_exec

# pattern STRB{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern STRB{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRB_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRB_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,1, core.Field(core.readR(t),7,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRB_i_T2_A_exec skipped')
    return aarch32_STRB_i_T2_A_exec

# pattern STRB{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern STRB{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern STRB{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_STRB_i_T3_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STRB_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111' or (P == '0' and W == '0'):
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if t == 15 or (wback and n == t):
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRB_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,1, core.Field(core.readR(t),7,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRB_i_T3_A_exec skipped')
    return aarch32_STRB_i_T3_A_exec


# instruction aarch32_STRB_r_A
# pattern STRB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_STRB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_STRB_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_STRB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.WriteMemU(address,1, core.Field(core.readR(t),7,0));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRB_r_T1_A_exec skipped')
    return aarch32_STRB_r_T1_A_exec

# pattern STRB{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern STRB{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_STRB_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STRB_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if t == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRB_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.WriteMemU(address,1, core.Field(core.readR(t),7,0));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRB_r_T2_A_exec skipped')
    return aarch32_STRB_r_T2_A_exec


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
            offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
            address = offset_addr if index else core.readR(n);
            if core.IsAligned(address, 8):
                data = 0;
                if True:
                    data = core.SetField(data,31,0,core.readR(t));
                    data = core.SetField(data,63,32,core.readR(t2));
                core.WriteMemA(address,8, data);
            else:
                core.WriteMemA(address,4, core.readR(t));
                core.WriteMemA(address+4,4, core.readR(t2));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRD_i_T1_A_exec skipped')
    return aarch32_STRD_i_T1_A_exec


# instruction aarch32_STREX_A
# pattern STREX{<c>}{<q>} <Rd>, <Rt>, [<Rn> {, #<imm>}] with bitdiffs=[]
# regex ^STREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$ : c Rd Rt Rn imm32*
def aarch32_STREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STREX_T1_A Rd={Rd} Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    if d == 15 or t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == n or d == t:
        raise Exception('UNPREDICTABLE');

    def aarch32_STREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) + imm32;
            if core.ExclusiveMonitorsPass(address,4):
                core.WriteMemA(address,4, core.readR(t));
                core.writeR(d, core.ZeroExtend('0', 32));
            else:
                core.writeR(d, core.ZeroExtend('1', 32));
        else:
            log.debug(f'aarch32_STREX_T1_A_exec skipped')
    return aarch32_STREX_T1_A_exec


# instruction aarch32_STREXB_A
# pattern STREXB{<c>}{<q>} <Rd>, <Rt>, [<Rn>] with bitdiffs=[]
# regex ^STREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rd Rt Rn
def aarch32_STREXB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_STREXB_T1_A Rd={Rd} Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if d == 15 or t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == n or d == t:
        raise Exception('UNPREDICTABLE');

    def aarch32_STREXB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            if core.ExclusiveMonitorsPass(address,1):
                core.WriteMemA(address,1, core.Field(core.readR(t),7,0));
                core.writeR(d, core.ZeroExtend('0', 32));
            else:
                core.writeR(d, core.ZeroExtend('1', 32));
        else:
            log.debug(f'aarch32_STREXB_T1_A_exec skipped')
    return aarch32_STREXB_T1_A_exec


# instruction aarch32_STREXH_A
# pattern STREXH{<c>}{<q>} <Rd>, <Rt>, [<Rn>] with bitdiffs=[]
# regex ^STREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rd Rt Rn
def aarch32_STREXH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_STREXH_T1_A Rd={Rd} Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if d == 15 or t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == n or d == t:
        raise Exception('UNPREDICTABLE');

    def aarch32_STREXH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            if core.ExclusiveMonitorsPass(address,2):
                core.WriteMemA(address,2, core.Field(core.readR(t),15,0));
                core.writeR(d, core.ZeroExtend('0', 32));
            else:
                core.writeR(d, core.ZeroExtend('1', 32));
        else:
            log.debug(f'aarch32_STREXH_T1_A_exec skipped')
    return aarch32_STREXH_T1_A_exec


# instruction aarch32_STRHT_A
# pattern STRHT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRHT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRHT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRHT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.readR(m) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            MemU_unpriv[address,2] = core.Field(core.readR(t),15,0);
            if postindex:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRHT_T1_A_exec skipped')
    return aarch32_STRHT_T1_A_exec


# instruction aarch32_STRH_i_A
# pattern STRH{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRH_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRH_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_STRH_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,2, core.Field(core.readR(t),15,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRH_i_T1_A_exec skipped')
    return aarch32_STRH_i_T1_A_exec

# pattern STRH{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern STRH{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRH_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRH_i_T2_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRH_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,2, core.Field(core.readR(t),15,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRH_i_T2_A_exec skipped')
    return aarch32_STRH_i_T2_A_exec

# pattern STRH{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern STRH{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern STRH{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_STRH_i_T3_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STRH_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111' or (P == '0' and W == '0'):
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if t == 15 or (wback and n == t):
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRH_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,2, core.Field(core.readR(t),15,0));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRH_i_T3_A_exec skipped')
    return aarch32_STRH_i_T3_A_exec


# instruction aarch32_STRH_r_A
# pattern STRH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_STRH_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_STRH_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_STRH_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.WriteMemU(address,2, core.Field(core.readR(t),15,0));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRH_r_T1_A_exec skipped')
    return aarch32_STRH_r_T1_A_exec

# pattern STRH{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern STRH{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_STRH_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STRH_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if t == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRH_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            core.WriteMemU(address,2, core.Field(core.readR(t),15,0));
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRH_r_T2_A_exec skipped')
    return aarch32_STRH_r_T2_A_exec


# instruction aarch32_STRT_A
# pattern STRT{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STRT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STRT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STRT_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  postindex = False;  add = True;
    register_form = False;  
    if t == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STRT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if core.APSR.EL == EL2:
                 raise Exception('UNPREDICTABLE');               # Hyp mode
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C) if register_form else imm32;
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = core.readR(n) if postindex else offset_addr;
            data = 0;
            if t == 15:
                  # Only possible for encodings A1 and A2
                data = core.PCStoreValue();
            else:
                data = core.readR(t);
            MemU_unpriv[address,4] = data;
            if postindex:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STRT_T1_A_exec skipped')
    return aarch32_STRT_T1_A_exec


# instruction aarch32_STR_i_A
# pattern STR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STR_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STR_i_T1_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;

    def aarch32_STR_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,4, core.readR(t));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_i_T1_A_exec skipped')
    return aarch32_STR_i_T1_A_exec

# pattern STR{<c>}{<q>} <Rt>, [SP{, #{+}<imm>}] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[SP(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt imm32*
def aarch32_STR_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STR_i_T2_A Rt={Rt} imm32={imm32} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = 13;  
    index = True;  add = True;  wback = False;

    def aarch32_STR_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,4, core.readR(t));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_i_T2_A_exec skipped')
    return aarch32_STR_i_T2_A_exec

# pattern STR{<c>}.W <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
# pattern STR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$ : c Rt Rn imm32*
def aarch32_STR_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STR_i_T3_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = True;  add = True;  wback = False;
    if t == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_STR_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,4, core.readR(t));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_i_T3_A_exec skipped')
    return aarch32_STR_i_T3_A_exec

# pattern STR{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=[('P', '1'), ('U', '0'), ('W', '0')]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$ : c Rt Rn imm32*
# pattern STR{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=[('P', '0'), ('W', '1')]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$ : c Rt Rn imm32
# pattern STR{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=[('P', '1'), ('W', '1')]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$ : c Rt Rn imm32
def aarch32_STR_i_T4_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STR_i_T4_A Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    if Rn == '1111' or (P == '0' and W == '0'):
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    index = (P == '1');  add = (U == '1');  wback = (W == '1');
    if t == 15 or (wback and n == t):
        raise Exception('UNPREDICTABLE');

    def aarch32_STR_i_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            if True:
                offset_addr = (core.readR(n) + imm32) if add else (core.readR(n) - imm32);
                address = offset_addr if index else core.readR(n);
                core.WriteMemU(address,4, core.readR(t));
                if wback:
                     core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_i_T4_A_exec skipped')
    return aarch32_STR_i_T4_A_exec


# instruction aarch32_STR_r_A
# pattern STR{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
def aarch32_STR_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_STR_r_T1_A Rt={Rt} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_STR_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = 0;
            if t == 15:
                  # Only possible for encoding A1
                data = core.PCStoreValue();
            else:
                data = core.readR(t);
            core.WriteMemU(address,4, data);
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_r_T1_A_exec skipped')
    return aarch32_STR_r_T1_A_exec

# pattern STR{<c>}.W <Rt>, [<Rn>, {+}<Rm>] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$ : c Rt Rn Rm
# pattern STR{<c>}{<q>} <Rt>, [<Rn>, {+}<Rm>{, LSL #<imm>}] with bitdiffs=[]
# regex ^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$ : c Rt Rn Rm shift_t* shift_n*
def aarch32_STR_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_STR_r_T2_A Rt={Rt} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    if Rn == '1111':
        raise Exception('UNDEFINED');
    t = core.reg_num[Rt];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    index = True;  add = True;  wback = False;
    if t == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_STR_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            offset = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            offset_addr = (core.readR(n) + offset) if add else (core.readR(n) - offset);
            address = offset_addr if index else core.readR(n);
            data = 0;
            if t == 15:
                  # Only possible for encoding A1
                data = core.PCStoreValue();
            else:
                data = core.readR(t);
            core.WriteMemU(address,4, data);
            if wback:
                 core.writeR(n, offset_addr);
        else:
            log.debug(f'aarch32_STR_r_T2_A_exec skipped')
    return aarch32_STR_r_T2_A_exec


# instruction aarch32_SUB_i_A
# pattern SUB<c>{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd Rn imm32
# pattern SUBS{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[('S', '1')]
# regex ^SUBS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : Rd Rn imm32
def aarch32_SUB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_SUB_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  

    def aarch32_SUB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T1_A_exec skipped')
    return aarch32_SUB_i_T1_A_exec

# pattern SUB<c>{<q>} <Rdn>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern SUB<c>{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$ : c Rdn imm32
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern SUBS{<q>} <Rdn>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
# pattern SUBS{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[('S', '1')]
# regex ^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$ : Rdn imm32
# regex ^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
def aarch32_SUB_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_SUB_i_T2_A Rdn={Rdn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rdn];  n = core.reg_num[Rdn];  setflags = (S == '1');  

    def aarch32_SUB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T2_A_exec skipped')
    return aarch32_SUB_i_T2_A_exec

# pattern SUB<c>.W {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern SUB{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern SUBS.W {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : Rd* Rn imm32
# pattern SUBS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_SUB_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SUB_i_T3_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');  
    if (d == 15 and not setflags) or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SUB_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T3_A_exec skipped')
    return aarch32_SUB_i_T3_A_exec

# pattern SUB{<c>}{<q>} {<Rd>,} <Rn>, #<imm12> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern SUBW{<c>}{<q>} {<Rd>,} <Rn>, #<imm12> with bitdiffs=[]
# regex ^SUBW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_SUB_i_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SUB_i_T4_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SUB_i_T4_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T4_A_exec skipped')
    return aarch32_SUB_i_T4_A_exec

# pattern SUBS{<c>}{<q>} PC, LR, #<imm8> with bitdiffs=[]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sPC,\sLR,\s#(?P<imm32>\d+)$ : c imm32
def aarch32_SUB_i_T5_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SUB_i_T5_AS imm32={imm32} cond={cond}')
    # decode
    d = 15;  n = core.reg_num[Rn];  setflags = True;  
    if n != 14:
        raise Exception('UNPREDICTABLE');

    def aarch32_SUB_i_T5_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.writeR(d, core.Field(result));
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T5_AS_exec skipped')
    return aarch32_SUB_i_T5_AS_exec


# instruction aarch32_SUB_r_A
# pattern SUB<c>{<q>} <Rd>, <Rn>, <Rm> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd Rn Rm
# pattern SUBS{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1')]
# regex ^SUBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
def aarch32_SUB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SUB_r_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_SUB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
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
            log.debug(f'aarch32_SUB_r_T1_A_exec skipped')
    return aarch32_SUB_r_T1_A_exec

# pattern SUB{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern SUB<c>.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
# pattern SUB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern SUBS{<c>}{<q>} {<Rd>,} <Rn>, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rn Rm shift_t
# pattern SUBS.W {<Rd>,} <Rn>, <Rm> with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
# pattern SUBS{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_SUB_r_T2_A(core, regex_match, bitdiffs):
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
    log.debug(f'aarch32_SUB_r_T2_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SUB_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(n), core.NOT(shifted), '1');
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
            log.debug(f'aarch32_SUB_r_T2_A_exec skipped')
    return aarch32_SUB_r_T2_A_exec


# instruction aarch32_SUB_SP_i_A
# pattern SUB{<c>}{<q>} {SP,} SP, #<imm7> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$ : c imm32
def aarch32_SUB_SP_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SUB_SP_i_T1_A imm32={imm32} cond={cond}')
    # decode
    d = 13;  setflags = False;  

    def aarch32_SUB_SP_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), core.NOT(imm32), '1');
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
            log.debug(f'aarch32_SUB_SP_i_T1_A_exec skipped')
    return aarch32_SUB_SP_i_T1_A_exec

# pattern SUB{<c>}.W {<Rd>,} SP, #<const> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern SUB{<c>}{<q>} {<Rd>,} SP, #<const> with bitdiffs=[('S', '0')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern SUBS{<c>}{<q>} {<Rd>,} SP, #<const> with bitdiffs=[('S', '1')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
def aarch32_SUB_SP_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_SUB_SP_i_T2_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  
    if d == 15 and not setflags:
        raise Exception('UNPREDICTABLE');

    def aarch32_SUB_SP_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), core.NOT(imm32), '1');
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
            log.debug(f'aarch32_SUB_SP_i_T2_A_exec skipped')
    return aarch32_SUB_SP_i_T2_A_exec

# pattern SUB{<c>}{<q>} {<Rd>,} SP, #<imm12> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
# pattern SUBW{<c>}{<q>} {<Rd>,} SP, #<imm12> with bitdiffs=[]
# regex ^SUBW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
def aarch32_SUB_SP_i_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SUB_SP_i_T3_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = False;  
    if d == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_SUB_SP_i_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.readR(13), core.NOT(imm32), '1');
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
            log.debug(f'aarch32_SUB_SP_i_T3_A_exec skipped')
    return aarch32_SUB_SP_i_T3_A_exec


# instruction aarch32_SUB_SP_r_A
# pattern SUB{<c>}{<q>} {<Rd>,} SP, <Rm>, RRX with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rm shift_t
# pattern SUB{<c>}.W {<Rd>,} SP, <Rm> with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$ : c Rd* Rm
# pattern SUB{<c>}{<q>} {<Rd>,} SP, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '0'), ('stype', '11')]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rm shift_t* shift_n*
# pattern SUBS{<c>}{<q>} {<Rd>,} SP, <Rm>, RRX with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rd* Rm shift_t
# pattern SUBS{<c>}{<q>} {<Rd>,} SP, <Rm> {, <shift> #<amount>} with bitdiffs=[('S', '1'), ('stype', '11')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rd* Rm shift_t* shift_n*
def aarch32_SUB_SP_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    S = bitdiffs.get('S', '0')
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SUB_SP_r_T1_A Rd={Rd} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  setflags = (S == '1');
    if (d == 15 and not setflags) or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SUB_SP_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.readR(13), core.NOT(shifted), '1');
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
            log.debug(f'aarch32_SUB_SP_r_T1_A_exec skipped')
    return aarch32_SUB_SP_r_T1_A_exec


# instruction aarch32_SVC_A
# pattern SVC{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^SVC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_SVC_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SVC_T1_A imm32={imm32} cond={cond}')
    # decode

    def aarch32_SVC_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.CheckForSVCTrap(core.Field(imm32,15,0));
            core.CallSupervisor(core.Field(imm32,15,0));
        else:
            log.debug(f'aarch32_SVC_T1_A_exec skipped')
    return aarch32_SVC_T1_A_exec


# instruction aarch32_SXTAB_A
# pattern SXTAB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTAB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_SXTAB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTAB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTAB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.readR(n) + core.SignExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_SXTAB_T1_A_exec skipped')
    return aarch32_SXTAB_T1_A_exec


# instruction aarch32_SXTAB16_A
# pattern SXTAB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTAB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_SXTAB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTAB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTAB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(core.readR(n),15,0) + core.SignExtend(core.Field(rotated,7,0), 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(core.readR(n),31,16) + core.SignExtend(core.Field(rotated,23,16), 16)));
        else:
            log.debug(f'aarch32_SXTAB16_T1_A_exec skipped')
    return aarch32_SXTAB16_T1_A_exec


# instruction aarch32_SXTAH_A
# pattern SXTAH{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTAH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_SXTAH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTAH_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTAH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.readR(n) + core.SignExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_SXTAH_T1_A_exec skipped')
    return aarch32_SXTAH_T1_A_exec


# instruction aarch32_SXTB_A
# pattern SXTB{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[]
# regex ^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
def aarch32_SXTB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_SXTB_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  rotation = 0;

    def aarch32_SXTB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SignExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_SXTB_T1_A_exec skipped')
    return aarch32_SXTB_T1_A_exec

# pattern SXTB{<c>}.W {<Rd>,} <Rm> with bitdiffs=[]
# regex ^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
# pattern SXTB{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_SXTB_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTB_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTB_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SignExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_SXTB_T2_A_exec skipped')
    return aarch32_SXTB_T2_A_exec


# instruction aarch32_SXTB16_A
# pattern SXTB16{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_SXTB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTB16_T1_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.SignExtend(core.Field(rotated,7,0), 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.SignExtend(core.Field(rotated,23,16), 16)));
        else:
            log.debug(f'aarch32_SXTB16_T1_A_exec skipped')
    return aarch32_SXTB16_T1_A_exec


# instruction aarch32_SXTH_A
# pattern SXTH{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[]
# regex ^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
def aarch32_SXTH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_SXTH_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  rotation = 0;

    def aarch32_SXTH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SignExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_SXTH_T1_A_exec skipped')
    return aarch32_SXTH_T1_A_exec

# pattern SXTH{<c>}.W {<Rd>,} <Rm> with bitdiffs=[]
# regex ^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
# pattern SXTH{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_SXTH_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SXTH_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SXTH_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SignExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_SXTH_T2_A_exec skipped')
    return aarch32_SXTH_T2_A_exec


# instruction aarch32_TBB_A
# pattern TBB{<c>}{<q>} [<Rn>, <Rm>] with bitdiffs=[('H', '0')]
# regex ^TBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+)\]$ : c Rn Rm
# pattern TBH{<c>}{<q>} [<Rn>, <Rm>, LSL #1] with bitdiffs=[('H', '1')]
# regex ^TBH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+),\sLSL\s#1\]$ : c Rn Rm
def aarch32_TBB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    H = bitdiffs.get('H', '0')
    log.debug(f'aarch32_TBB_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];  is_tbh = (H == '1');
    if m == 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_TBB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            halfwords = 0;
            if is_tbh:
                halfwords = core.UInt(core.ReadMemU(core.readR(n)+core.LSL(core.readR(m),1), 2));
            else:
                halfwords = core.UInt(core.ReadMemU(core.readR(n)+core.readR(m), 1));
            core.BranchWritePC(core.PC + 2*halfwords, 'INDIR');
        else:
            log.debug(f'aarch32_TBB_T1_A_exec skipped')
    return aarch32_TBB_T1_A_exec


# instruction aarch32_TEQ_i_A
# pattern TEQ{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_TEQ_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_TEQ_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];
    carry = core.APSR.C;
    if n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_TEQ_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) ^ imm32;
            core.APSR.N = core.Bit(result,31);
            core.APSR.Z = core.IsZeroBit(result);
            core.APSR.C = carry;
            # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_TEQ_i_T1_A_exec skipped')
    return aarch32_TEQ_i_T1_A_exec


# instruction aarch32_TEQ_r_A
# pattern TEQ{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern TEQ{<c>}{<q>} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('stype', '11')]
# regex ^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rn Rm shift_t* shift_n*
def aarch32_TEQ_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_TEQ_r_T1_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_TEQ_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) ^ shifted;
            core.APSR.N = core.Bit(result,31);
            core.APSR.Z = core.IsZeroBit(result);
            core.APSR.C = carry;
            # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_TEQ_r_T1_A_exec skipped')
    return aarch32_TEQ_r_T1_A_exec


# instruction aarch32_TST_i_A
# pattern TST{<c>}{<q>} <Rn>, #<const> with bitdiffs=[]
# regex ^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rn imm32
def aarch32_TST_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_TST_i_T1_A Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    n = core.reg_num[Rn];
    carry = core.APSR.C;
    if n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_TST_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.readR(n) & imm32;
            core.APSR.N = core.Bit(result,31);
            core.APSR.Z = core.IsZeroBit(result);
            core.APSR.C = carry;
            # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_TST_i_T1_A_exec skipped')
    return aarch32_TST_i_T1_A_exec


# instruction aarch32_TST_r_A
# pattern TST{<c>}{<q>} <Rn>, <Rm> with bitdiffs=[]
# regex ^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
def aarch32_TST_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_TST_r_T1_A Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_TST_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & shifted;
            core.APSR.N = core.Bit(result,31);
            core.APSR.Z = core.IsZeroBit(result);
            core.APSR.C = carry;
            # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_TST_r_T1_A_exec skipped')
    return aarch32_TST_r_T1_A_exec

# pattern TST{<c>}{<q>} <Rn>, <Rm>, RRX with bitdiffs=[('stype', '11')]
# regex ^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$ : c Rn Rm shift_t
# pattern TST{<c>}.W <Rn>, <Rm> with bitdiffs=[('stype', '11')]
# regex ^TST(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rn Rm
# pattern TST{<c>}{<q>} <Rn>, <Rm> {, <shift> #<amount>} with bitdiffs=[('stype', '11')]
# regex ^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$ : c Rn Rm shift_t* shift_n*
def aarch32_TST_r_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    stype = bitdiffs.get('stype', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_TST_r_T2_A Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_TST_r_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (shifted, carry) = core.Shift_C(core.readR(m), shift_t, shift_n, core.APSR.C);
            result = core.readR(n) & shifted;
            core.APSR.N = core.Bit(result,31);
            core.APSR.Z = core.IsZeroBit(result);
            core.APSR.C = carry;
            # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_TST_r_T2_A_exec skipped')
    return aarch32_TST_r_T2_A_exec


# instruction aarch32_UADD16_A
# pattern UADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),15,0));
            sum2 = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum1,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum2,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if sum1 >= 0x10000 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum2 >= 0x10000 else '00');
        else:
            log.debug(f'aarch32_UADD16_T1_A_exec skipped')
    return aarch32_UADD16_T1_A_exec


# instruction aarch32_UADD8_A
# pattern UADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m  == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),7,0)) + core.UInt(core.Field(core.readR(m),7,0));
            sum2 = core.UInt(core.Field(core.readR(n),15,8)) + core.UInt(core.Field(core.readR(m),15,8));
            sum3 = core.UInt(core.Field(core.readR(n),23,16)) + core.UInt(core.Field(core.readR(m),23,16));
            sum4 = core.UInt(core.Field(core.readR(n),31,24)) + core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,7,0)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,7,0)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,7,0)));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if sum1 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if sum2 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if sum3 >= 0x100 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if sum4 >= 0x100 else '0')
        else:
            log.debug(f'aarch32_UADD8_T1_A_exec skipped')
    return aarch32_UADD8_T1_A_exec


# instruction aarch32_UASX_A
# pattern UASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),31,16));
            sum  = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if sum  >= 0x10000 else '00');
        else:
            log.debug(f'aarch32_UASX_T1_A_exec skipped')
    return aarch32_UASX_T1_A_exec


# instruction aarch32_UBFX_A
# pattern UBFX{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^UBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_UBFX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_UBFX_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];
    lsbit = core.UInt(lsb);  
    msbit = core.UInt(width) - 1 + core.UInt(lsb);
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit > 31:
        msbit = 31;

    def aarch32_UBFX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.writeR(d, core.ZeroExtendSubField(core.readR(n), msbit, lsbit, 32));
        else:
            log.debug(f'aarch32_UBFX_T1_A_exec skipped')
    return aarch32_UBFX_T1_A_exec


# instruction aarch32_UDF_A
# pattern UDF{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_UDF_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_UDF_T1_A imm32={imm32} cond={cond}')
    # decode
    # imm32 is for assembly and disassembly only, and is ignored by hardware.

    def aarch32_UDF_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            raise Exception('UNDEFINED');
        else:
            log.debug(f'aarch32_UDF_T1_A_exec skipped')
    return aarch32_UDF_T1_A_exec

# pattern UDF{<c>}.W {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?.W\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
# pattern UDF{<c>}{<q>} {#}<imm> with bitdiffs=[]
# regex ^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : c imm32
def aarch32_UDF_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_UDF_T2_A imm32={imm32} cond={cond}')
    # decode
    # imm32 is for assembly and disassembly only, and is ignored by hardware.

    def aarch32_UDF_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            raise Exception('UNDEFINED');
        else:
            log.debug(f'aarch32_UDF_T2_A_exec skipped')
    return aarch32_UDF_T2_A_exec


# instruction aarch32_UDIV_A
# pattern UDIV{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UDIV_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UDIV_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = 15;
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == 15 or n == 15 or m == 15 or a != 15:
        raise Exception('UNPREDICTABLE');

    def aarch32_UDIV_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = 0;
            if core.UInt(core.R[m]) == 0:
                result = 0;
            else:
                result = core.RoundTowardsZero(core.Real(core.UInt(core.readR(n))) / core.Real(core.UInt(core.readR(m))));
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_UDIV_T1_A_exec skipped')
    return aarch32_UDIV_T1_A_exec


# instruction aarch32_UHADD16_A
# pattern UHADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),15,0));
            sum2 = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum1,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum2,16,1)));
        else:
            log.debug(f'aarch32_UHADD16_T1_A_exec skipped')
    return aarch32_UHADD16_T1_A_exec


# instruction aarch32_UHADD8_A
# pattern UHADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),7,0)) + core.UInt(core.Field(core.readR(m),7,0));
            sum2 = core.UInt(core.Field(core.readR(n),15,8)) + core.UInt(core.Field(core.readR(m),15,8));
            sum3 = core.UInt(core.Field(core.readR(n),23,16)) + core.UInt(core.Field(core.readR(m),23,16));
            sum4 = core.UInt(core.Field(core.readR(n),31,24)) + core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(sum1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(sum2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(sum3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(sum4,8,1)));
        else:
            log.debug(f'aarch32_UHADD8_T1_A_exec skipped')
    return aarch32_UHADD8_T1_A_exec


# instruction aarch32_UHASX_A
# pattern UHASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),31,16));
            sum  = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(sum,16,1)));
        else:
            log.debug(f'aarch32_UHASX_T1_A_exec skipped')
    return aarch32_UHASX_T1_A_exec


# instruction aarch32_UHSAX_A
# pattern UHSAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHSAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHSAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHSAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),31,16));
            diff = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff,16,1)));
        else:
            log.debug(f'aarch32_UHSAX_T1_A_exec skipped')
    return aarch32_UHSAX_T1_A_exec


# instruction aarch32_UHSUB16_A
# pattern UHSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),15,0));
            diff2 = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff1,16,1)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff2,16,1)));
        else:
            log.debug(f'aarch32_UHSUB16_T1_A_exec skipped')
    return aarch32_UHSUB16_T1_A_exec


# instruction aarch32_UHSUB8_A
# pattern UHSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UHSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UHSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UHSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),7,0)) - core.UInt(core.Field(core.readR(m),7,0));
            diff2 = core.UInt(core.Field(core.readR(n),15,8)) - core.UInt(core.Field(core.readR(m),15,8));
            diff3 = core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16));
            diff4 = core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(diff1,8,1)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(diff2,8,1)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(diff3,8,1)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(diff4,8,1)));
        else:
            log.debug(f'aarch32_UHSUB8_T1_A_exec skipped')
    return aarch32_UHSUB8_T1_A_exec


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


# instruction aarch32_UMLAL_A
# pattern UMLAL{<c>}{<q>} <RdLo>, <RdHi>, <Rn>, <Rm> with bitdiffs=[]
# regex ^UMLAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c RdLo RdHi Rn Rm
def aarch32_UMLAL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    RdLo = regex_groups.get('RdLo', None)
    RdHi = regex_groups.get('RdHi', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_UMLAL_T1_A RdLo={RdLo} RdHi={RdHi} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    dLo = core.reg_num[RdLo];  dHi = core.reg_num[RdHi];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = False;
    if dLo == 15 or dHi == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE');
    # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if dHi == dLo:
        raise Exception('UNPREDICTABLE');

    def aarch32_UMLAL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.UInt(core.readR(n)) * core.UInt(core.readR(m)) + core.UInt(core.readR(dLo), core.readR(dHi));
            core.writeR(dHi, core.Field(result,63,32));
            core.writeR(dLo, core.Field(result,31,0));
            if setflags:
                core.APSR.N = core.Bit(result,63);
                core.APSR.Z = core.IsZeroBit(core.Field(result,63,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_UMLAL_T1_A_exec skipped')
    return aarch32_UMLAL_T1_A_exec


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


# instruction aarch32_UQADD16_A
# pattern UQADD16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQADD16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQADD16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQADD16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),15,0));
            sum2 = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.UnsignedSat(sum1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.UnsignedSat(sum2, 16)));
        else:
            log.debug(f'aarch32_UQADD16_T1_A_exec skipped')
    return aarch32_UQADD16_T1_A_exec


# instruction aarch32_UQADD8_A
# pattern UQADD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQADD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQADD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQADD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum1 = core.UInt(core.Field(core.readR(n),7,0)) + core.UInt(core.Field(core.readR(m),7,0));
            sum2 = core.UInt(core.Field(core.readR(n),15,8)) + core.UInt(core.Field(core.readR(m),15,8));
            sum3 = core.UInt(core.Field(core.readR(n),23,16)) + core.UInt(core.Field(core.readR(m),23,16));
            sum4 = core.UInt(core.Field(core.readR(n),31,24)) + core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.UnsignedSat(sum1, 8)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.UnsignedSat(sum2, 8)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.UnsignedSat(sum3, 8)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.UnsignedSat(sum4, 8)));
        else:
            log.debug(f'aarch32_UQADD8_T1_A_exec skipped')
    return aarch32_UQADD8_T1_A_exec


# instruction aarch32_UQASX_A
# pattern UQASX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQASX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQASX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQASX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),31,16));
            sum  = core.UInt(core.Field(core.readR(n),31,16)) + core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.UnsignedSat(diff, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.UnsignedSat(sum, 16)));
        else:
            log.debug(f'aarch32_UQASX_T1_A_exec skipped')
    return aarch32_UQASX_T1_A_exec


# instruction aarch32_UQSAX_A
# pattern UQSAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQSAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQSAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQSAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),31,16));
            diff = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.UnsignedSat(sum, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.UnsignedSat(diff, 16)));
        else:
            log.debug(f'aarch32_UQSAX_T1_A_exec skipped')
    return aarch32_UQSAX_T1_A_exec


# instruction aarch32_UQSUB16_A
# pattern UQSUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQSUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQSUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQSUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),15,0));
            diff2 = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.UnsignedSat(diff1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.UnsignedSat(diff2, 16)));
        else:
            log.debug(f'aarch32_UQSUB16_T1_A_exec skipped')
    return aarch32_UQSUB16_T1_A_exec


# instruction aarch32_UQSUB8_A
# pattern UQSUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^UQSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_UQSUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_UQSUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UQSUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),7,0)) - core.UInt(core.Field(core.readR(m),7,0));
            diff2 = core.UInt(core.Field(core.readR(n),15,8)) - core.UInt(core.Field(core.readR(m),15,8));
            diff3 = core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16));
            diff4 = core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.UnsignedSat(diff1, 8)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.UnsignedSat(diff2, 8)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.UnsignedSat(diff3, 8)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.UnsignedSat(diff4, 8)));
        else:
            log.debug(f'aarch32_UQSUB8_T1_A_exec skipped')
    return aarch32_UQSUB8_T1_A_exec


# instruction aarch32_USAD8_A
# pattern USAD8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^USAD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_USAD8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_USAD8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAD8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            absdiff1 = core.Abs(core.UInt(core.Field(core.readR(n),7,0))   - core.UInt(core.Field(core.readR(m),7,0)));
            absdiff2 = core.Abs(core.UInt(core.Field(core.readR(n),15,8))  - core.UInt(core.Field(core.readR(m),15,8)));
            absdiff3 = core.Abs(core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16)));
            absdiff4 = core.Abs(core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24)));
            result = absdiff1 + absdiff2 + absdiff3 + absdiff4;
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_USAD8_T1_A_exec skipped')
    return aarch32_USAD8_T1_A_exec


# instruction aarch32_USADA8_A
# pattern USADA8{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[]
# regex ^USADA8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_USADA8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    log.debug(f'aarch32_USADA8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USADA8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            absdiff1 = core.Abs(core.UInt(core.Field(core.readR(n),7,0))   - core.UInt(core.Field(core.readR(m),7,0)));
            absdiff2 = core.Abs(core.UInt(core.Field(core.readR(n),15,8))  - core.UInt(core.Field(core.readR(m),15,8)));
            absdiff3 = core.Abs(core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16)));
            absdiff4 = core.Abs(core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24)));
            result = core.UInt(core.readR(a)) + absdiff1 + absdiff2 + absdiff3 + absdiff4;
            core.writeR(d, core.Field(result,31,0));
        else:
            log.debug(f'aarch32_USADA8_T1_A_exec skipped')
    return aarch32_USADA8_T1_A_exec


# instruction aarch32_USAT_A
# pattern USAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, ASR #<amount> with bitdiffs=[('sh', '1')]
# regex ^USAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$ : c Rd imm32 Rn shift_t shift_n
# pattern USAT{<c>}{<q>} <Rd>, #<imm>, <Rn> {, LSL #<amount>} with bitdiffs=[('sh', '0')]
# regex ^USAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$ : c Rd imm32 Rn shift_t* shift_n*
def aarch32_USAT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    sh = bitdiffs.get('sh', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_USAT_T1_A Rd={Rd} imm32={imm32} Rn={Rn} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand = core.Shift(core.readR(n), shift_t, shift_n, core.APSR.C);  # core.APSR.C ignored
            (result, sat) = core.UnsignedSatQ(core.SInt(operand), imm32);
            core.writeR(d, core.ZeroExtend(result, 32));
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_USAT_T1_A_exec skipped')
    return aarch32_USAT_T1_A_exec


# instruction aarch32_USAT16_A
# pattern USAT16{<c>}{<q>} <Rd>, #<imm>, <Rn> with bitdiffs=[]
# regex ^USAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$ : c Rd imm32 Rn
def aarch32_USAT16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_USAT16_T1_A Rd={Rd} imm32={imm32} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAT16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result1, sat1) = core.UnsignedSatQ(core.SInt(core.Field(core.readR(n),15,0)), imm32);
            (result2, sat2) = core.UnsignedSatQ(core.SInt(core.Field(core.readR(n),31,16)), imm32);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.ZeroExtend(result1, 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.ZeroExtend(result2, 16)));
            if sat1 or sat2:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_USAT16_T1_A_exec skipped')
    return aarch32_USAT16_T1_A_exec


# instruction aarch32_USAX_A
# pattern USAX{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^USAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_USAX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_USAX_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USAX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            sum  = core.UInt(core.Field(core.readR(n),15,0)) + core.UInt(core.Field(core.readR(m),31,16));
            diff = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),15,0));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(sum,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if sum  >= 0x10000 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if diff >= 0 else '00');
        else:
            log.debug(f'aarch32_USAX_T1_A_exec skipped')
    return aarch32_USAX_T1_A_exec


# instruction aarch32_USUB16_A
# pattern USUB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^USUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_USUB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_USUB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USUB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),15,0)) - core.UInt(core.Field(core.readR(m),15,0));
            diff2 = core.UInt(core.Field(core.readR(n),31,16)) - core.UInt(core.Field(core.readR(m),31,16));
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(diff1,15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(diff2,15,0)));
            core.APSR.GE = core.SetField(core.APSR.GE,1,0,'11' if diff1 >= 0 else '00');
            core.APSR.GE = core.SetField(core.APSR.GE,3,2,'11' if diff2 >= 0 else '00');
        else:
            log.debug(f'aarch32_USUB16_T1_A_exec skipped')
    return aarch32_USUB16_T1_A_exec


# instruction aarch32_USUB8_A
# pattern USUB8{<c>}{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^USUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd* Rn Rm
def aarch32_USUB8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_USUB8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USUB8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            diff1 = core.UInt(core.Field(core.readR(n),7,0)) - core.UInt(core.Field(core.readR(m),7,0));
            diff2 = core.UInt(core.Field(core.readR(n),15,8)) - core.UInt(core.Field(core.readR(m),15,8));
            diff3 = core.UInt(core.Field(core.readR(n),23,16)) - core.UInt(core.Field(core.readR(m),23,16));
            diff4 = core.UInt(core.Field(core.readR(n),31,24)) - core.UInt(core.Field(core.readR(m),31,24));
            core.writeR(d, core.SetField(core.readR(d),7,0,core.Field(diff1,7,0)));
            core.writeR(d, core.SetField(core.readR(d),15,8,core.Field(diff2,7,0)));
            core.writeR(d, core.SetField(core.readR(d),23,16,core.Field(diff3,7,0)));
            core.writeR(d, core.SetField(core.readR(d),31,24,core.Field(diff4,7,0)));
            core.APSR.GE = core.SetBit(core.APSR.GE,0,'1' if diff1 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,1,'1' if diff2 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,2,'1' if diff3 >= 0 else '0')
            core.APSR.GE = core.SetBit(core.APSR.GE,3,'1' if diff4 >= 0 else '0')
        else:
            log.debug(f'aarch32_USUB8_T1_A_exec skipped')
    return aarch32_USUB8_T1_A_exec


# instruction aarch32_UXTAB_A
# pattern UXTAB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTAB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_UXTAB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTAB_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTAB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.readR(n) + core.ZeroExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_UXTAB_T1_A_exec skipped')
    return aarch32_UXTAB_T1_A_exec


# instruction aarch32_UXTAB16_A
# pattern UXTAB16{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTAB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_UXTAB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTAB16_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTAB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(core.readR(n),15,0) + core.ZeroExtend(core.Field(rotated,7,0), 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(core.readR(n),31,16) + core.ZeroExtend(core.Field(rotated,23,16), 16)));
        else:
            log.debug(f'aarch32_UXTAB16_T1_A_exec skipped')
    return aarch32_UXTAB16_T1_A_exec


# instruction aarch32_UXTAH_A
# pattern UXTAH{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTAH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rn Rm shift_t* rotation*
def aarch32_UXTAH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if Rd is None:
        Rd = Rn
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTAH_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTAH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.readR(n) + core.ZeroExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_UXTAH_T1_A_exec skipped')
    return aarch32_UXTAH_T1_A_exec


# instruction aarch32_UXTB_A
# pattern UXTB{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[]
# regex ^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
def aarch32_UXTB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_UXTB_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  rotation = 0;

    def aarch32_UXTB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.ZeroExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_UXTB_T1_A_exec skipped')
    return aarch32_UXTB_T1_A_exec

# pattern UXTB{<c>}.W {<Rd>,} <Rm> with bitdiffs=[]
# regex ^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
# pattern UXTB{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_UXTB_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTB_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTB_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.ZeroExtend(core.Field(rotated,7,0), 32));
        else:
            log.debug(f'aarch32_UXTB_T2_A_exec skipped')
    return aarch32_UXTB_T2_A_exec


# instruction aarch32_UXTB16_A
# pattern UXTB16{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_UXTB16_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTB16_T1_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTB16_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.SetField(core.readR(d),15,0,core.ZeroExtend(core.Field(rotated,7,0), 16)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.ZeroExtend(core.Field(rotated,23,16), 16)));
        else:
            log.debug(f'aarch32_UXTB16_T1_A_exec skipped')
    return aarch32_UXTB16_T1_A_exec


# instruction aarch32_UXTH_A
# pattern UXTH{<c>}{<q>} {<Rd>,} <Rm> with bitdiffs=[]
# regex ^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
def aarch32_UXTH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    log.debug(f'aarch32_UXTH_T1_A Rd={Rd} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  rotation = 0;

    def aarch32_UXTH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.ZeroExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_UXTH_T1_A_exec skipped')
    return aarch32_UXTH_T1_A_exec

# pattern UXTH{<c>}.W {<Rd>,} <Rm> with bitdiffs=[]
# regex ^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$ : c Rd* Rm
# pattern UXTH{<c>}{<q>} {<Rd>,} <Rm> {, ROR #<amount>} with bitdiffs=[]
# regex ^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$ : c Rd* Rm shift_t* rotation*
def aarch32_UXTH_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    rotation = regex_groups.get('rotation', None)
    if rotation is None:
        rotation = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_UXTH_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} rotation={rotation} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  
    if d == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_UXTH_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            rotated = core.ROR(core.readR(m), rotation);
            core.writeR(d, core.ZeroExtend(core.Field(rotated,15,0), 32));
        else:
            log.debug(f'aarch32_UXTH_T2_A_exec skipped')
    return aarch32_UXTH_T2_A_exec


patterns = {
    'ADC': [
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {'S': '0'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {'S': '0'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADC_i_T1_A, {'S': '0'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADC_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'ADCS': [
        (re.compile(r'^ADCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {'S': '1'}),
        (re.compile(r'^ADCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T1_A, {'S': '1'}),
        (re.compile(r'^ADCS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADC_i_T1_A, {'S': '1'}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADC_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'ADD': [
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP,\s(?P<Rdm>\w+)$', re.I), aarch32_ADD_SP_r_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_ADD_SP_r_T2_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\sSP,\s(?P=Rdm)$', re.I), aarch32_ADD_SP_r_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T2_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sSP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T4_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T4_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
    ],
    'ADDS': [
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T1_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T1_A, {'S': '1'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
    ],
    'ADDW': [
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T3_A, {'S': '0'}),
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T4_A, {}),
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T4_A, {}),
    ],
    'ADR': [
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T1_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T2_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
    ],
    'AND': [
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {'S': '0'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {'S': '0'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_AND_i_T1_A, {'S': '0'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^AND(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_AND_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'ANDS': [
        (re.compile(r'^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {'S': '1'}),
        (re.compile(r'^ANDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T1_A, {'S': '1'}),
        (re.compile(r'^ANDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_AND_i_T1_A, {'S': '1'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ANDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_AND_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'ASR': [
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ASR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
    'ASRS': [
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ASR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'B': [
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T3_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T4_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T1_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T2_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T3_A, {}),
        (re.compile(r'^B(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_B_T4_A, {}),
    ],
    'BFC': [
        (re.compile(r'^BFC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_BFC_T1_A, {}),
    ],
    'BFI': [
        (re.compile(r'^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_BFI_T1_A, {}),
    ],
    'BIC': [
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T1_A, {'S': '0'}),
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T1_A, {'S': '0'}),
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_BIC_i_T1_A, {'S': '0'}),
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_BIC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^BIC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_BIC_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'BICS': [
        (re.compile(r'^BICS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T1_A, {'S': '1'}),
        (re.compile(r'^BICS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T1_A, {'S': '1'}),
        (re.compile(r'^BICS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_BIC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_BIC_i_T1_A, {'S': '1'}),
        (re.compile(r'^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_BIC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^BICS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_BIC_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'BKPT': [
        (re.compile(r'^BKPT(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_BKPT_T1_A, {}),
    ],
    'BL': [
        (re.compile(r'^BL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_BL_i_T1_A, {}),
    ],
    'BLX': [
        (re.compile(r'^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$', re.I), aarch32_BLX_r_T1_A, {}),
        (re.compile(r'^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_BL_i_T2_A, {}),
    ],
    'BX': [
        (re.compile(r'^BX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$', re.I), aarch32_BX_T1_A, {}),
    ],
    'CBNZ': [
        (re.compile(r'^CBNZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_CBNZ_T1_A, {'op': '1'}),
    ],
    'CBZ': [
        (re.compile(r'^CBZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_CBNZ_T1_A, {'op': '0'}),
    ],
    'CLREX': [
        (re.compile(r'^CLREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$', re.I), aarch32_CLREX_T1_A, {}),
    ],
    'CLZ': [
        (re.compile(r'^CLZ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CLZ_T1_A, {}),
    ],
    'CMN': [
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMN_r_T1_A, {}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMN_i_T1_A, {}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
        (re.compile(r'^CMN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_CMN_r_T2_A, {'stype': '11'}),
    ],
    'CMP': [
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T1_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_CMP_r_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T1_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_CMP_i_T2_A, {}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
        (re.compile(r'^CMP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+)$', re.I), aarch32_CMP_r_T3_A, {'stype': '11'}),
    ],
    'EOR': [
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T1_A, {'S': '0'}),
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T1_A, {'S': '0'}),
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_EOR_i_T1_A, {'S': '0'}),
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_EOR_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^EOR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_EOR_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'EORS': [
        (re.compile(r'^EORS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T1_A, {'S': '1'}),
        (re.compile(r'^EORS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T1_A, {'S': '1'}),
        (re.compile(r'^EORS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_EOR_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_EOR_i_T1_A, {'S': '1'}),
        (re.compile(r'^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_EOR_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^EORS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_EOR_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'IT': [
        (re.compile(r'^IT(?P<mask>[ET]*)(?:\.[NW])?\s(?P<firstcond>\w\w)$', re.I), aarch32_IT_T1_A, {}),
    ],
    'LDM': [
        (re.compile(r'^LDM(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_POP_T1_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T1_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T1_A, {}),
        (re.compile(r'^LDM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
    ],
    'LDMDB': [
        (re.compile(r'^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
        (re.compile(r'^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
    ],
    'LDMEA': [
        (re.compile(r'^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
        (re.compile(r'^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
    ],
    'LDMFD': [
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T1_A, {}),
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T1_A, {}),
        (re.compile(r'^LDMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDM_T2_A, {}),
    ],
    'LDR': [
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDR_l_T2_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[SP(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDR_i_T2_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDR_l_T2_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDR_l_T1_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDR_l_T2_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDR_r_T2_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDR_i_T3_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDR_r_T1_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDR_i_T4_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDR_i_T4_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDR_i_T4_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDR_i_T1_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDR_i_T3_A, {}),
        (re.compile(r'^LDR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDR_r_T2_A, {}),
    ],
    'LDRB': [
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRB_l_T1_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRB_l_T1_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRB_r_T2_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRB_i_T2_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRB_r_T1_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRB_i_T3_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDRB_i_T3_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRB_i_T3_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRB_i_T1_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRB_i_T2_A, {}),
        (re.compile(r'^LDRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDRB_r_T2_A, {}),
    ],
    'LDRBT': [
        (re.compile(r'^LDRBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRBT_T1_A, {}),
    ],
    'LDRD': [
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRD_l_T1_A, {'P': '0', 'W': '0'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRD_l_T1_A, {'P': '0', 'W': '0'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRD_i_T1_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRD_i_T1_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$', re.I), aarch32_LDRD_i_T1_A, {'P': '1', 'W': '0'}),
    ],
    'LDREX': [
        (re.compile(r'^LDREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$', re.I), aarch32_LDREX_T1_A, {}),
    ],
    'LDREXB': [
        (re.compile(r'^LDREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_LDREXB_T1_A, {}),
    ],
    'LDREXH': [
        (re.compile(r'^LDREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_LDREXH_T1_A, {}),
    ],
    'LDRH': [
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRH_l_T1_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRH_l_T1_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRH_r_T2_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRH_i_T2_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRH_r_T1_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRH_i_T3_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDRH_i_T3_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRH_i_T3_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRH_i_T1_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRH_i_T2_A, {}),
        (re.compile(r'^LDRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDRH_r_T2_A, {}),
    ],
    'LDRHT': [
        (re.compile(r'^LDRHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRHT_T1_A, {}),
    ],
    'LDRSB': [
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRSB_l_T1_A, {}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRSB_l_T1_A, {}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSB_r_T2_A, {}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSB_r_T1_A, {}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRSB_i_T2_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDRSB_i_T2_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRSB_i_T2_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSB_i_T1_A, {}),
        (re.compile(r'^LDRSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDRSB_r_T2_A, {}),
    ],
    'LDRSBT': [
        (re.compile(r'^LDRSBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSBT_T1_A, {}),
    ],
    'LDRSH': [
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC,\s#(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDRSH_l_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_LDRSH_l_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSH_r_T2_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_LDRSH_r_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDRSH_i_T2_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDRSH_i_T2_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDRSH_i_T2_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSH_i_T1_A, {}),
        (re.compile(r'^LDRSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_LDRSH_r_T2_A, {}),
    ],
    'LDRSHT': [
        (re.compile(r'^LDRSHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRSHT_T1_A, {}),
    ],
    'LDRT': [
        (re.compile(r'^LDRT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDRT_T1_A, {}),
    ],
    'LSL': [
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSL)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
    'LSLS': [
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSL)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'LSR': [
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>LSR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
    'LSRS': [
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>LSR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'MLA': [
        (re.compile(r'^MLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_MLA_T1_A, {}),
    ],
    'MLS': [
        (re.compile(r'^MLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_MLS_T1_A, {}),
    ],
    'MOV': [
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T1_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T3_A, {}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\sLSL\s#0)?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111', 'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '0', 'stype': '11'}),
    ],
    'MOVS': [
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T1_A, {'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011', 'S': '1'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111', 'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MOV_r_T3_A, {'S': '1', 'stype': '11'}),
    ],
    'MOVT': [
        (re.compile(r'^MOVT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOVT_T1_A, {}),
    ],
    'MOVW': [
        (re.compile(r'^MOVW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOV_i_T3_A, {}),
    ],
    'MRS': [
        (re.compile(r'^MRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<spec_reg>\w+)$', re.I), aarch32_MRS_T1_AS, {}),
    ],
    'MSR': [
        (re.compile(r'^MSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<spec_reg>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_MSR_r_T1_AS, {}),
    ],
    'MUL': [
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$', re.I), aarch32_MUL_T1_A, {'S': '0'}),
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$', re.I), aarch32_MUL_T2_A, {}),
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$', re.I), aarch32_MUL_T2_A, {}),
    ],
    'MULS': [
        (re.compile(r'^MULS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$', re.I), aarch32_MUL_T1_A, {'S': '1'}),
    ],
    'MVN': [
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T1_A, {'S': '0'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MVN_i_T1_A, {'S': '0'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^MVN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MVN_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'MVNS': [
        (re.compile(r'^MVNS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MVNS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_MVN_r_T1_A, {'S': '1'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MVN_i_T1_A, {'S': '1'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^MVNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_MVN_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'NEG': [
        (re.compile(r'^NEG(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$', re.I), aarch32_RSB_i_T1_A, {'S': '0'}),
    ],
    'NEGS': [
        (re.compile(r'^NEGS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+)$', re.I), aarch32_RSB_i_T1_A, {'S': '1'}),
    ],
    'NOP': [
        (re.compile(r'^NOP(?P<c>[ACEGHLMNPV][CEILQST])?.W$', re.I), aarch32_NOP_T2_A, {}),
        (re.compile(r'^NOP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?$', re.I), aarch32_NOP_T1_A, {}),
    ],
    'ORN': [
        (re.compile(r'^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORN_i_T1_A, {'S': '0'}),
        (re.compile(r'^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ORN_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ORN_r_T1_A, {'S': '0', 'stype': '11'}),
    ],
    'ORNS': [
        (re.compile(r'^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORN_i_T1_A, {'S': '1'}),
        (re.compile(r'^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ORN_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ORN_r_T1_A, {'S': '1', 'stype': '11'}),
    ],
    'ORR': [
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T1_A, {'S': '0'}),
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T1_A, {'S': '0'}),
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORR_i_T1_A, {'S': '0'}),
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ORR_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ORR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ORR_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'ORRS': [
        (re.compile(r'^ORRS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T1_A, {'S': '1'}),
        (re.compile(r'^ORRS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T1_A, {'S': '1'}),
        (re.compile(r'^ORRS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ORR_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORR_i_T1_A, {'S': '1'}),
        (re.compile(r'^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ORR_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ORRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ORR_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'PKHBT': [
        (re.compile(r'^PKHBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$', re.I), aarch32_PKH_T1_A, {'tb': '0'}),
    ],
    'PKHTB': [
        (re.compile(r'^PKHTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+))?$', re.I), aarch32_PKH_T1_A, {'tb': '1'}),
    ],
    'POP': [
        (re.compile(r'^POP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_POP_T1_A, {}),
    ],
    'PUSH': [
        (re.compile(r'^PUSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_PUSH_T1_A, {}),
    ],
    'QADD': [
        (re.compile(r'^QADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QADD_T1_A, {}),
    ],
    'QADD16': [
        (re.compile(r'^QADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QADD16_T1_A, {}),
    ],
    'QADD8': [
        (re.compile(r'^QADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QADD8_T1_A, {}),
    ],
    'QASX': [
        (re.compile(r'^QASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QASX_T1_A, {}),
    ],
    'QDADD': [
        (re.compile(r'^QDADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QDADD_T1_A, {}),
    ],
    'QDSUB': [
        (re.compile(r'^QDSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QDSUB_T1_A, {}),
    ],
    'QSAX': [
        (re.compile(r'^QSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QSAX_T1_A, {}),
    ],
    'QSUB': [
        (re.compile(r'^QSUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_QSUB_T1_A, {}),
    ],
    'QSUB16': [
        (re.compile(r'^QSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QSUB16_T1_A, {}),
    ],
    'QSUB8': [
        (re.compile(r'^QSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_QSUB8_T1_A, {}),
    ],
    'RBIT': [
        (re.compile(r'^RBIT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_RBIT_T1_A, {}),
    ],
    'REV': [
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T2_A, {}),
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T1_A, {}),
        (re.compile(r'^REV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV_T2_A, {}),
    ],
    'REV16': [
        (re.compile(r'^REV16(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV16_T2_A, {}),
        (re.compile(r'^REV16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV16_T1_A, {}),
        (re.compile(r'^REV16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REV16_T2_A, {}),
    ],
    'REVSH': [
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T2_A, {}),
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T1_A, {}),
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T2_A, {}),
    ],
    'ROR': [
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^(?P<shift_t>ROR)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
    'RORS': [
        (re.compile(r'^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^(?P<shift_t>ROR)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+),\s#(?P<shift_n>\d+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'RRX': [
        (re.compile(r'^(?P<shift_t>RRX)(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T3_A, {'S': '0'}),
    ],
    'RRXS': [
        (re.compile(r'^(?P<shift_t>RRX)S(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_MOV_r_T3_A, {'S': '1'}),
    ],
    'RSB': [
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T2_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T1_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_RSB_i_T2_A, {'S': '0'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_RSB_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^RSB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_RSB_r_T1_A, {'S': '0', 'stype': '11'}),
    ],
    'RSBS': [
        (re.compile(r'^RSBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T2_A, {'S': '1'}),
        (re.compile(r'^RSBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#0$', re.I), aarch32_RSB_i_T1_A, {'S': '1'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_RSB_i_T2_A, {'S': '1'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_RSB_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^RSBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_RSB_r_T1_A, {'S': '1', 'stype': '11'}),
    ],
    'SADD16': [
        (re.compile(r'^SADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SADD16_T1_A, {}),
    ],
    'SADD8': [
        (re.compile(r'^SADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SADD8_T1_A, {}),
    ],
    'SASX': [
        (re.compile(r'^SASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SASX_T1_A, {}),
    ],
    'SBC': [
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T1_A, {'S': '0'}),
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T1_A, {'S': '0'}),
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SBC_i_T1_A, {'S': '0'}),
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SBC_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SBC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SBC_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'SBCS': [
        (re.compile(r'^SBCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T1_A, {'S': '1'}),
        (re.compile(r'^SBCS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T1_A, {'S': '1'}),
        (re.compile(r'^SBCS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SBC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SBC_i_T1_A, {'S': '1'}),
        (re.compile(r'^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SBC_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SBCS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SBC_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'SBFX': [
        (re.compile(r'^SBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_SBFX_T1_A, {}),
    ],
    'SDIV': [
        (re.compile(r'^SDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SDIV_T1_A, {}),
    ],
    'SEL': [
        (re.compile(r'^SEL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SEL_T1_A, {}),
    ],
    'SHADD16': [
        (re.compile(r'^SHADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHADD16_T1_A, {}),
    ],
    'SHADD8': [
        (re.compile(r'^SHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHADD8_T1_A, {}),
    ],
    'SHASX': [
        (re.compile(r'^SHASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHASX_T1_A, {}),
    ],
    'SHSAX': [
        (re.compile(r'^SHSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHSAX_T1_A, {}),
    ],
    'SHSUB16': [
        (re.compile(r'^SHSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHSUB16_T1_A, {}),
    ],
    'SHSUB8': [
        (re.compile(r'^SHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SHSUB8_T1_A, {}),
    ],
    'SMLABB': [
        (re.compile(r'^SMLABB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMLABT': [
        (re.compile(r'^SMLABT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMLAD': [
        (re.compile(r'^SMLAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAD_T1_A, {'M': '0'}),
    ],
    'SMLADX': [
        (re.compile(r'^SMLADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAD_T1_A, {'M': '1'}),
    ],
    'SMLAL': [
        (re.compile(r'^SMLAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLAL_T1_A, {}),
    ],
    'SMLALBB': [
        (re.compile(r'^SMLALBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMLALBT': [
        (re.compile(r'^SMLALBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMLALD': [
        (re.compile(r'^SMLALD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALD_T1_A, {'M': '0'}),
    ],
    'SMLALDX': [
        (re.compile(r'^SMLALDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALD_T1_A, {'M': '1'}),
    ],
    'SMLALTB': [
        (re.compile(r'^SMLALTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMLALTT': [
        (re.compile(r'^SMLALTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLALBB_T1_A, {'N': '1', 'M': '1'}),
    ],
    'SMLATB': [
        (re.compile(r'^SMLATB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMLATT': [
        (re.compile(r'^SMLATT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLABB_T1_A, {'N': '1', 'M': '1'}),
    ],
    'SMLAWB': [
        (re.compile(r'^SMLAWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAWB_T1_A, {'M': '0'}),
    ],
    'SMLAWT': [
        (re.compile(r'^SMLAWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLAWB_T1_A, {'M': '1'}),
    ],
    'SMLSD': [
        (re.compile(r'^SMLSD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLSD_T1_A, {'M': '0'}),
    ],
    'SMLSDX': [
        (re.compile(r'^SMLSDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMLSD_T1_A, {'M': '1'}),
    ],
    'SMLSLD': [
        (re.compile(r'^SMLSLD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLSLD_T1_A, {'M': '0'}),
    ],
    'SMLSLDX': [
        (re.compile(r'^SMLSLDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMLSLD_T1_A, {'M': '1'}),
    ],
    'SMMLA': [
        (re.compile(r'^SMMLA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLA_T1_A, {'R': '0'}),
    ],
    'SMMLAR': [
        (re.compile(r'^SMMLAR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLA_T1_A, {'R': '1'}),
    ],
    'SMMLS': [
        (re.compile(r'^SMMLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLS_T1_A, {'R': '0'}),
    ],
    'SMMLSR': [
        (re.compile(r'^SMMLSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_SMMLS_T1_A, {'R': '1'}),
    ],
    'SMMUL': [
        (re.compile(r'^SMMUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMMUL_T1_A, {'R': '0'}),
    ],
    'SMMULR': [
        (re.compile(r'^SMMULR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMMUL_T1_A, {'R': '1'}),
    ],
    'SMUAD': [
        (re.compile(r'^SMUAD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUAD_T1_A, {'M': '0'}),
    ],
    'SMUADX': [
        (re.compile(r'^SMUADX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUAD_T1_A, {'M': '1'}),
    ],
    'SMULBB': [
        (re.compile(r'^SMULBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '0', 'M': '0'}),
    ],
    'SMULBT': [
        (re.compile(r'^SMULBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '0', 'M': '1'}),
    ],
    'SMULL': [
        (re.compile(r'^SMULL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULL_T1_A, {}),
    ],
    'SMULTB': [
        (re.compile(r'^SMULTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '1', 'M': '0'}),
    ],
    'SMULTT': [
        (re.compile(r'^SMULTT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULBB_T1_A, {'N': '1', 'M': '1'}),
    ],
    'SMULWB': [
        (re.compile(r'^SMULWB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULWB_T1_A, {'M': '0'}),
    ],
    'SMULWT': [
        (re.compile(r'^SMULWT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMULWB_T1_A, {'M': '1'}),
    ],
    'SMUSD': [
        (re.compile(r'^SMUSD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUSD_T1_A, {'M': '0'}),
    ],
    'SMUSDX': [
        (re.compile(r'^SMUSDX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SMUSD_T1_A, {'M': '1'}),
    ],
    'SSAT': [
        (re.compile(r'^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$', re.I), aarch32_SSAT_T1_A, {'sh': '1'}),
        (re.compile(r'^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$', re.I), aarch32_SSAT_T1_A, {'sh': '0'}),
    ],
    'SSAT16': [
        (re.compile(r'^SSAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$', re.I), aarch32_SSAT16_T1_A, {}),
    ],
    'SSAX': [
        (re.compile(r'^SSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SSAX_T1_A, {}),
    ],
    'SSUB16': [
        (re.compile(r'^SSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SSUB16_T1_A, {}),
    ],
    'SSUB8': [
        (re.compile(r'^SSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SSUB8_T1_A, {}),
    ],
    'STM': [
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T1_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STM(?:IA)?(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
    ],
    'STMDB': [
        (re.compile(r'^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_PUSH_T1_A, {}),
        (re.compile(r'^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
        (re.compile(r'^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
    ],
    'STMEA': [
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T1_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
        (re.compile(r'^STMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STM_T2_A, {}),
    ],
    'STMFD': [
        (re.compile(r'^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
        (re.compile(r'^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?P<wback>!),\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
    ],
    'STR': [
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[SP(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STR_i_T2_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STR_r_T2_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STR_i_T3_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STR_r_T1_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_STR_i_T4_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_STR_i_T4_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_STR_i_T4_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STR_i_T1_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STR_i_T3_A, {}),
        (re.compile(r'^STR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_STR_r_T2_A, {}),
    ],
    'STRB': [
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STRB_r_T2_A, {}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRB_i_T2_A, {}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STRB_r_T1_A, {}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_STRB_i_T3_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_STRB_i_T3_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_STRB_i_T3_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRB_i_T1_A, {}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRB_i_T2_A, {}),
        (re.compile(r'^STRB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_STRB_r_T2_A, {}),
    ],
    'STRBT': [
        (re.compile(r'^STRBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRBT_T1_A, {}),
    ],
    'STRD': [
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_STRD_i_T1_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_STRD_i_T1_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^STRD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s(?P<Rt2>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+-]?\d+))?\]$', re.I), aarch32_STRD_i_T1_A, {'P': '1', 'W': '0'}),
    ],
    'STREX': [
        (re.compile(r'^STREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$', re.I), aarch32_STREX_T1_A, {}),
    ],
    'STREXB': [
        (re.compile(r'^STREXB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_STREXB_T1_A, {}),
    ],
    'STREXH': [
        (re.compile(r'^STREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_STREXH_T1_A, {}),
    ],
    'STRH': [
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STRH_r_T2_A, {}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRH_i_T2_A, {}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)\]$', re.I), aarch32_STRH_r_T1_A, {}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_STRH_i_T3_A, {'P': '0', 'W': '1'}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_STRH_i_T3_A, {'P': '1', 'U': '0', 'W': '0'}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_STRH_i_T3_A, {'P': '1', 'W': '1'}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRH_i_T1_A, {}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRH_i_T2_A, {}),
        (re.compile(r'^STRH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s[+]?(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?\]$', re.I), aarch32_STRH_r_T2_A, {}),
    ],
    'STRHT': [
        (re.compile(r'^STRHT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRHT_T1_A, {}),
    ],
    'STRT': [
        (re.compile(r'^STRT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_STRT_T1_A, {}),
    ],
    'SUB': [
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T1_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sPC,\s#(?P<imm32>\d+)$', re.I), aarch32_ADR_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T3_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T1_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T1_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T4_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'SUBS': [
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sPC,\sLR,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T5_AS, {}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '1'}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '1'}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {'S': '1'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '1'}),
        (re.compile(r'^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '1'}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T1_A, {'S': '1'}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T1_A, {'S': '1'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '1'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'SUBW': [
        (re.compile(r'^SUBW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T3_A, {}),
        (re.compile(r'^SUBW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T4_A, {}),
    ],
    'SVC': [
        (re.compile(r'^SVC(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_SVC_T1_A, {}),
    ],
    'SXTAB': [
        (re.compile(r'^SXTAB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTAB_T1_A, {}),
    ],
    'SXTAB16': [
        (re.compile(r'^SXTAB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTAB16_T1_A, {}),
    ],
    'SXTAH': [
        (re.compile(r'^SXTAH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTAH_T1_A, {}),
    ],
    'SXTB': [
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTB_T2_A, {}),
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTB_T1_A, {}),
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTB_T2_A, {}),
    ],
    'SXTB16': [
        (re.compile(r'^SXTB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTB16_T1_A, {}),
    ],
    'SXTH': [
        (re.compile(r'^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTH_T2_A, {}),
        (re.compile(r'^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTH_T1_A, {}),
        (re.compile(r'^SXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTH_T2_A, {}),
    ],
    'TBB': [
        (re.compile(r'^TBB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+)\]$', re.I), aarch32_TBB_T1_A, {'H': '0'}),
    ],
    'TBH': [
        (re.compile(r'^TBH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\[(?P<Rn>\w+),\s(?P<Rm>\w+),\sLSL\s#1\]$', re.I), aarch32_TBB_T1_A, {'H': '1'}),
    ],
    'TEQ': [
        (re.compile(r'^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_TEQ_i_T1_A, {}),
        (re.compile(r'^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_TEQ_r_T1_A, {'stype': '11'}),
        (re.compile(r'^TEQ(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_TEQ_r_T1_A, {'stype': '11'}),
    ],
    'TST': [
        (re.compile(r'^TST(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_TST_r_T2_A, {'stype': '11'}),
        (re.compile(r'^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_TST_r_T1_A, {}),
        (re.compile(r'^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_TST_i_T1_A, {}),
        (re.compile(r'^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_TST_r_T2_A, {'stype': '11'}),
        (re.compile(r'^TST(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_TST_r_T2_A, {'stype': '11'}),
    ],
    'UADD16': [
        (re.compile(r'^UADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UADD16_T1_A, {}),
    ],
    'UADD8': [
        (re.compile(r'^UADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UADD8_T1_A, {}),
    ],
    'UASX': [
        (re.compile(r'^UASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UASX_T1_A, {}),
    ],
    'UBFX': [
        (re.compile(r'^UBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_UBFX_T1_A, {}),
    ],
    'UDF': [
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?.W\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T2_A, {}),
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T1_A, {}),
        (re.compile(r'^UDF(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_UDF_T2_A, {}),
    ],
    'UDIV': [
        (re.compile(r'^UDIV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UDIV_T1_A, {}),
    ],
    'UHADD16': [
        (re.compile(r'^UHADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHADD16_T1_A, {}),
    ],
    'UHADD8': [
        (re.compile(r'^UHADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHADD8_T1_A, {}),
    ],
    'UHASX': [
        (re.compile(r'^UHASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHASX_T1_A, {}),
    ],
    'UHSAX': [
        (re.compile(r'^UHSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHSAX_T1_A, {}),
    ],
    'UHSUB16': [
        (re.compile(r'^UHSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHSUB16_T1_A, {}),
    ],
    'UHSUB8': [
        (re.compile(r'^UHSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UHSUB8_T1_A, {}),
    ],
    'UMAAL': [
        (re.compile(r'^UMAAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UMAAL_T1_A, {}),
    ],
    'UMLAL': [
        (re.compile(r'^UMLAL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UMLAL_T1_A, {}),
    ],
    'UMULL': [
        (re.compile(r'^UMULL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<RdLo>\w+),\s(?P<RdHi>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UMULL_T1_A, {}),
    ],
    'UQADD16': [
        (re.compile(r'^UQADD16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQADD16_T1_A, {}),
    ],
    'UQADD8': [
        (re.compile(r'^UQADD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQADD8_T1_A, {}),
    ],
    'UQASX': [
        (re.compile(r'^UQASX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQASX_T1_A, {}),
    ],
    'UQSAX': [
        (re.compile(r'^UQSAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQSAX_T1_A, {}),
    ],
    'UQSUB16': [
        (re.compile(r'^UQSUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQSUB16_T1_A, {}),
    ],
    'UQSUB8': [
        (re.compile(r'^UQSUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_UQSUB8_T1_A, {}),
    ],
    'USAD8': [
        (re.compile(r'^USAD8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_USAD8_T1_A, {}),
    ],
    'USADA8': [
        (re.compile(r'^USADA8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_USADA8_T1_A, {}),
    ],
    'USAT': [
        (re.compile(r'^USAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$', re.I), aarch32_USAT_T1_A, {'sh': '1'}),
        (re.compile(r'^USAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$', re.I), aarch32_USAT_T1_A, {'sh': '0'}),
    ],
    'USAT16': [
        (re.compile(r'^USAT16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)$', re.I), aarch32_USAT16_T1_A, {}),
    ],
    'USAX': [
        (re.compile(r'^USAX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_USAX_T1_A, {}),
    ],
    'USUB16': [
        (re.compile(r'^USUB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_USUB16_T1_A, {}),
    ],
    'USUB8': [
        (re.compile(r'^USUB8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_USUB8_T1_A, {}),
    ],
    'UXTAB': [
        (re.compile(r'^UXTAB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTAB_T1_A, {}),
    ],
    'UXTAB16': [
        (re.compile(r'^UXTAB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTAB16_T1_A, {}),
    ],
    'UXTAH': [
        (re.compile(r'^UXTAH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTAH_T1_A, {}),
    ],
    'UXTB': [
        (re.compile(r'^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_UXTB_T2_A, {}),
        (re.compile(r'^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_UXTB_T1_A, {}),
        (re.compile(r'^UXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTB_T2_A, {}),
    ],
    'UXTB16': [
        (re.compile(r'^UXTB16(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTB16_T1_A, {}),
    ],
    'UXTH': [
        (re.compile(r'^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_UXTH_T2_A, {}),
        (re.compile(r'^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_UXTH_T1_A, {}),
        (re.compile(r'^UXTH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTH_T2_A, {}),
    ],
}
