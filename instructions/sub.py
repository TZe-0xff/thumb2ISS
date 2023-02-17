import re, logging

log = logging.getLogger('Mnem.SUB')
# instruction aarch32_SUB_i_A
# pattern SUB<c>{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd Rn imm32
# pattern SUBS{<q>} <Rd>, <Rn>, #<imm3> with bitdiffs=[]
# regex ^SUBS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : Rd Rn imm32
def aarch32_SUB_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SUB_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = not core.InITBlock();  

    def aarch32_SUB_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T1_A_exec skipped')
    return aarch32_SUB_i_T1_A_exec

# pattern SUB<c>{<q>} <Rdn>, #<imm8> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern SUB<c>{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : c Rdn imm32
# pattern SUBS{<q>} <Rdn>, #<imm8> with bitdiffs=[]
# regex ^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
# pattern SUBS{<q>} {<Rdn>,} <Rdn>, #<imm8> with bitdiffs=[]
# regex ^SUBS(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s#(?P<imm32>\d+)$ : Rdn imm32
def aarch32_SUB_i_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdn = regex_groups.get('Rdn', None)
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_SUB_i_T2_A Rdn={Rdn} imm32={imm32} cond={cond}')
    # decode
    d = core.UInt(Rdn);  n = core.UInt(Rdn);  setflags = not core.InITBlock();  

    def aarch32_SUB_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
    d = bitdiffs.get('d', '0')
    n = bitdiffs.get('n', '0')
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
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T3_A_exec skipped')
    return aarch32_SUB_i_T3_A_exec

# pattern SUB{<c>}{<q>} {<Rd>,} <Rn>, #<imm12> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_SUB_i_T4_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    n = bitdiffs.get('n', '0')
    n = bitdiffs.get('n', '0')
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
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T4_A_exec skipped')
    return aarch32_SUB_i_T4_A_exec

# pattern SUBS{<c>}{<q>} PC, LR, #<imm8> with bitdiffs=[('!(Rn', '1110')]
# regex ^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sPC,\sLR,\s#(?P<imm32>\d+)$ : c imm32
def aarch32_SUB_i_T5_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    imm32 = regex_groups.get('imm32', None)
    !(Rn = bitdiffs.get('!(Rn', '0')
    n = bitdiffs.get('n', '0')
    log.debug(f'aarch32_SUB_i_T5_AS imm32={imm32} cond={cond}')
    # decode
    d = 15;  n = core.reg_num[Rn];  setflags = True;  
    if n != 14:
        raise Exception('UNPREDICTABLE');
    if core.InITBlock() and not core.LastInITBlock():
        raise Exception('UNPREDICTABLE');

    def aarch32_SUB_i_T5_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(imm32), '1');
            if d == 15:
                if setflags:
                    core.ALUExceptionReturn(result);
                else:
                    core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
                if setflags:
                    core.APSR.update(nzcv);
        else:
            log.debug(f'aarch32_SUB_i_T5_AS_exec skipped')
    return aarch32_SUB_i_T5_AS_exec


# instruction aarch32_SUB_r_A
# pattern SUB<c>{<q>} <Rd>, <Rn>, <Rm> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$ : c Rd Rn Rm
# pattern SUBS{<q>} {<Rd>,} <Rn>, <Rm> with bitdiffs=[]
# regex ^SUBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$ : Rd* Rn Rm
def aarch32_SUB_r_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_SUB_r_T1_A Rd={Rd} Rn={Rn} Rm={Rm} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  setflags = not core.InITBlock();
    (shift_t, shift_n) = ('LSL', 0);

    def aarch32_SUB_r_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(shifted), '1');
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
    d = bitdiffs.get('d', '0')
    n = bitdiffs.get('n', '0')
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
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[n], core.NOT(shifted), '1');
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
            (result, nzcv) = core.AddWithCarry(core.R[13], core.NOT(imm32), '1');
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
    d = bitdiffs.get('d', '0')
    log.debug(f'aarch32_SUB_SP_i_T2_A Rd={Rd} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  setflags = (S == '1');  
    if d == 15 and not setflags:
        raise Exception('UNPREDICTABLE');

    def aarch32_SUB_SP_i_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[13], core.NOT(imm32), '1');
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
            log.debug(f'aarch32_SUB_SP_i_T2_A_exec skipped')
    return aarch32_SUB_SP_i_T2_A_exec

# pattern SUB{<c>}{<q>} {<Rd>,} SP, #<imm12> with bitdiffs=[]
# regex ^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$ : c Rd* imm32
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
            (result, nzcv) = core.AddWithCarry(core.R[13], core.NOT(imm32), '1');
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
    d = bitdiffs.get('d', '0')
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
            shifted = core.Shift(core.R[m], shift_t, shift_n, core.APSR.C);
            (result, nzcv) = core.AddWithCarry(core.R[13], core.NOT(shifted), '1');
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
            log.debug(f'aarch32_SUB_SP_r_T1_A_exec skipped')
    return aarch32_SUB_SP_r_T1_A_exec


patterns = {
    'SUB': [
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:SP,\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T1_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T3_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T1_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '0'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T4_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T1_A, {}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '0', 'stype': '11'}),
        (re.compile(r'^SUB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_r_T2_A, {'S': '0', 'stype': '11'}),
    ],
    'SUBS': [
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?:(?:\w+),\s)?(?P<Rdn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T2_A, {}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sPC,\sLR,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T5_AS, {'!(Rn': '1110'}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T1_A, {}),
        (re.compile(r'^SUBS(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T1_A, {}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_SP_i_T2_A, {'S': '1'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '1'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>RRX)$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?SP,\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_SP_r_T1_A, {'S': '1', 'stype': '11'}),
        (re.compile(r'^SUBS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+))?$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
    'SUBS.W ': [
        (re.compile(r'^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_SUB_i_T3_A, {'S': '1'}),
        (re.compile(r'^SUBS.W\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_SUB_r_T2_A, {'S': '1', 'stype': '11'}),
    ],
}
