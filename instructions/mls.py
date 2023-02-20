import re, logging

log = logging.getLogger('Mnem.MLS')
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
            operand1 = core.SInt(core.R[n]);  # operand1 = core.UInt(core.R[n]) produces the same final results
            operand2 = core.SInt(core.R[m]);  # operand2 = core.UInt(core.R[m]) produces the same final results
            addend   = core.SInt(core.R[a]);  # addend   = core.UInt(core.R[a]) produces the same final results
            result = addend - operand1 * operand2;
            core.R[d] = core.Field(result,31,0);
        else:
            log.debug(f'aarch32_MLS_T1_A_exec skipped')
    return aarch32_MLS_T1_A_exec


patterns = {
    'MLS': [
        (re.compile(r'^MLS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_MLS_T1_A, {}),
    ],
}
