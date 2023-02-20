import re, logging

log = logging.getLogger('Mnem.MULS')
# instruction aarch32_MUL_A
# pattern MUL<c>{<q>} <Rdm>, <Rn>{, <Rdm>} with bitdiffs=[]
# regex ^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$ : c Rdm Rn
# pattern MULS{<q>} <Rdm>, <Rn>{, <Rdm>} with bitdiffs=[]
# regex ^MULS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$ : Rdm Rn
def aarch32_MUL_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_MUL_T1_A Rdm={Rdm} Rn={Rn} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  n = core.reg_num[Rn];  m = core.reg_num[Rdm];  setflags = not (cond is not None);

    def aarch32_MUL_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.R[n]) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.R[m]) produces the same final results
            result = operand1 * operand2;
            core.R[d] = core.Field(result,31,0);
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
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.R[n]) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.R[m]) produces the same final results
            result = operand1 * operand2;
            core.R[d] = core.Field(result,31,0);
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(core.Field(result,31,0));
                # core.APSR.C, core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MUL_T2_A_exec skipped')
    return aarch32_MUL_T2_A_exec


patterns = {
    'MUL': [
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$', re.I), aarch32_MUL_T1_A, {}),
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$', re.I), aarch32_MUL_T2_A, {}),
        (re.compile(r'^MUL(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+)(?:,\s(?P<Rm>\w+))?$', re.I), aarch32_MUL_T2_A, {}),
    ],
    'MULS': [
        (re.compile(r'^MULS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P<Rn>\w+)(?:,\s(?P=Rdm))?$', re.I), aarch32_MUL_T1_A, {}),
    ],
}
