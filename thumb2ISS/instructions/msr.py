import re, logging

log = logging.getLogger('Mnem.MSR')
# instruction aarch32_MSR_br_AS

# instruction aarch32_MSR_r_AS
# pattern MSR{<c>}{<q>} <spec_reg>, <Rn> with bitdiffs=[]
# regex ^MSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<spec_reg>\w+),\s(?P<Rn>\w+)$ : c spec_reg Rn
def aarch32_MSR_r_T1_AS(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    spec_reg = regex_groups.get('spec_reg', None)
    Rn = regex_groups.get('Rn', None)
    R = bitdiffs.get('R', '0')
    log.debug(f'aarch32_MSR_r_T1_AS spec_reg={spec_reg} Rn={Rn} cond={cond}')
    # decode
    n = core.reg_num[Rn];  
    if n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MSR_r_T1_AS_exec():
        # execute
        if core.ConditionPassed(cond):
            core.WriteSpecReg(spec_reg, core.readR(n));
        else:
            log.debug(f'aarch32_MSR_r_T1_AS_exec skipped')
    return aarch32_MSR_r_T1_AS_exec


patterns = {
    'MSR': [
        (re.compile(r'^MSR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<spec_reg>\w+),\s(?P<Rn>\w+)$', re.I), aarch32_MSR_r_T1_AS, {}),
    ],
}
