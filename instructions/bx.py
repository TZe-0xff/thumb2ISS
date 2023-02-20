import re, logging

log = logging.getLogger('Mnem.BX')
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
            core.BXWritePC(core.R[m], 'INDIR');
        else:
            log.debug(f'aarch32_BX_T1_A_exec skipped')
    return aarch32_BX_T1_A_exec


patterns = {
    'BX': [
        (re.compile(r'^BX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rm>\w+)$', re.I), aarch32_BX_T1_A, {}),
    ],
}
