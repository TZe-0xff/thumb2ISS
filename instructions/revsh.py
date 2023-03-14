import re, logging

log = logging.getLogger('Mnem.REVSH')
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
            result = core.SetField(result,31,8,core.SignExtend(core.Field(core.R[m],7,0), 24));
            result = core.SetField(result,7,0,core.Field(core.R[m],15,8));
            core.R[d] = core.Field(result); log.info(f'Setting R{d}={hex(core.UInt(result))}')
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
            result = core.SetField(result,31,8,core.SignExtend(core.Field(core.R[m],7,0), 24));
            result = core.SetField(result,7,0,core.Field(core.R[m],15,8));
            core.R[d] = core.Field(result); log.info(f'Setting R{d}={hex(core.UInt(result))}')
        else:
            log.debug(f'aarch32_REVSH_T2_A_exec skipped')
    return aarch32_REVSH_T2_A_exec


patterns = {
    'REVSH': [
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T1_A, {}),
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T2_A, {}),
        (re.compile(r'^REVSH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+)$', re.I), aarch32_REVSH_T2_A, {}),
    ],
}
