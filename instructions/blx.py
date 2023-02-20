import re, logging

log = logging.getLogger('Mnem.BLX')
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
            target = core.R[m];
            core.BXWritePC(target, 'INDCALL');
        else:
            log.debug(f'aarch32_BLX_r_T1_A_exec skipped')
    return aarch32_BLX_r_T1_A_exec


patterns = {
    'BLX': [
        (re.compile(r'^BLX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$', re.I), aarch32_BLX_r_T1_A, {}),
    ],
}
