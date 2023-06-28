import re, logging

log = logging.getLogger('Mnem.SXTB')
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


patterns = {
    'SXTB': [
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTB_T1_A, {}),
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)$', re.I), aarch32_SXTB_T2_A, {}),
        (re.compile(r'^SXTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rm>\w+)(?:,\s(?P<shift_t>ROR)\s#(?P<rotation>\d+))?$', re.I), aarch32_SXTB_T2_A, {}),
    ],
}
