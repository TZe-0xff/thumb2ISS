import re, logging

log = logging.getLogger('Mnem.LDREXH')
# instruction aarch32_LDREXH_A
# pattern LDREXH{<c>}{<q>} <Rt>, [<Rn>] with bitdiffs=[]
# regex ^LDREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$ : c Rt Rn
def aarch32_LDREXH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    log.debug(f'aarch32_LDREXH_T1_A Rt={Rt} Rn={Rn} cond={cond}')
    # decode
    t = core.reg_num[Rt];  n = core.reg_num[Rn];
    if t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_LDREXH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n);
            core.SetExclusiveMonitors(address,2);
            core.writeR(t, core.ZeroExtend(core.ReadMemA(address,2), 32));
        else:
            log.debug(f'aarch32_LDREXH_T1_A_exec skipped')
    return aarch32_LDREXH_T1_A_exec


patterns = {
    'LDREXH': [
        (re.compile(r'^LDREXH(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\]$', re.I), aarch32_LDREXH_T1_A, {}),
    ],
}
