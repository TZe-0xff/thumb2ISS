import re, logging

log = logging.getLogger('Mnem.STREX')
# instruction aarch32_STREX_A
# pattern STREX{<c>}{<q>} <Rd>, <Rt>, [<Rn> {, #<imm>}] with bitdiffs=[]
# regex ^STREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$ : c Rd Rt Rn imm32*
def aarch32_STREX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rt = regex_groups.get('Rt', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_STREX_T1_A Rd={Rd} Rt={Rt} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  t = core.reg_num[Rt];  n = core.reg_num[Rn];  
    if d == 15 or t == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if d == n or d == t:
        raise Exception('UNPREDICTABLE');

    def aarch32_STREX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(n) + imm32;
            if core.ExclusiveMonitorsPass(address,4):
                core.WriteMemA(address,4, core.readR(t));
                core.writeR(d, core.ZeroExtend('0', 32));
            else:
                core.writeR(d, core.ZeroExtend('1', 32));
        else:
            log.debug(f'aarch32_STREX_T1_A_exec skipped')
    return aarch32_STREX_T1_A_exec


patterns = {
    'STREX': [
        (re.compile(r'^STREX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>\d+))?\]$', re.I), aarch32_STREX_T1_A, {}),
    ],
}
