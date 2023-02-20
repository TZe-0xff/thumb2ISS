import re, logging

log = logging.getLogger('Mnem.MRS')
# instruction aarch32_MRS_AS
# pattern MRS{<c>}{<q>} <Rd>, <spec_reg> with bitdiffs=[]
# regex ^MRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<spec_reg>\w+)$ : c Rd spec_reg
def aarch32_MRS_T1_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    spec_reg = regex_groups.get('spec_reg', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_MRS_T1_AS Rd={Rd} spec_reg={spec_reg} cond={cond}')
    # decode
    d = core.reg_num[Rd];  
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MRS_T1_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            core.R[d] = core.ReadSpecReg(spec_reg);
        else:
            log.debug(f'aarch32_MRS_T1_AS_exec skipped')
    return aarch32_MRS_T1_AS_exec


# instruction aarch32_MRS_br_AS

patterns = {
    'MRS': [
        (re.compile(r'^MRS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<spec_reg>\w+)$', re.I), aarch32_MRS_T1_AS, {}),
    ],
}
