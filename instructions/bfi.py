import re, logging

log = logging.getLogger('Mnem.BFI')
# instruction aarch32_BFI_A
# pattern BFI{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_BFI_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_BFI_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  msbit = core.UInt(width) + core.UInt(lsb);  lsbit = core.UInt(lsb);
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit < lsbit:
        raise Exception('UNPREDICTABLE');

    def aarch32_BFI_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            tmp_Rd = core.R[d] & ~((0xffffffff >> (31 - msbit + lsbit)) << lsbit);
            core.R[d] = tmp_Rd | (core.UInt(core.R[n]) << lsbit);
            # Other bits of core.R[d] are unchanged
        else:
            log.debug(f'aarch32_BFI_T1_A_exec skipped')
    return aarch32_BFI_T1_A_exec


patterns = {
    'BFI': [
        (re.compile(r'^BFI(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_BFI_T1_A, {}),
    ],
}
