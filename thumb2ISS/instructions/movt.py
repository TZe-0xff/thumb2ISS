import re, logging

log = logging.getLogger('Mnem.MOVT')
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


patterns = {
    'MOVT': [
        (re.compile(r'^MOVT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_MOVT_T1_A, {}),
    ],
}
