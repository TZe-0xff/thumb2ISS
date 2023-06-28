import re, logging

log = logging.getLogger('Mnem.ADD')
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


patterns = {
    'ADD': [
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T2_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\sSP,\s(?P=Rdm)$', re.I), aarch32_ADD_SP_r_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP,\s(?P<Rdm>\w+)$', re.I), aarch32_ADD_SP_r_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_ADD_SP_r_T2_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T2_A, {'DN': '1'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\sSP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T1_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T4_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T4_A, {}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T1_A, {'S': '0'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^ADD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_r_T3_A, {'S': '0', 'stype': '11'}),
    ],
    'ADDS': [
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s(?P=Rdn),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T2_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T1_A, {'S': '1'}),
        (re.compile(r'^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T1_A, {'S': '1'}),
        (re.compile(r'^ADDS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T3_A, {'S': '1'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_SP_r_T3_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^ADDS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_ADD_r_T3_A, {'S': '1', 'stype': '11'}),
    ],
    'ADDW': [
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_SP_i_T4_A, {}),
        (re.compile(r'^ADDW(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ADD_i_T4_A, {}),
    ],
}
