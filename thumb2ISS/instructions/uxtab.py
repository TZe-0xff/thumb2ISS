import re, logging

log = logging.getLogger('Mnem.UXTAB')
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
            core.R[d] = core.readR(n) + core.ZeroExtend(core.Field(rotated,7,0), 32);
        else:
            log.debug(f'aarch32_UXTAB_T1_A_exec skipped')
    return aarch32_UXTAB_T1_A_exec


patterns = {
    'UXTAB': [
        (re.compile(r'^UXTAB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_UXTAB_T1_A, {}),
    ],
}
