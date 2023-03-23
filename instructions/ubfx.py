import re, logging

log = logging.getLogger('Mnem.UBFX')
# instruction aarch32_UBFX_A
# pattern UBFX{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width> with bitdiffs=[]
# regex ^UBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$ : c Rd Rn lsb width
def aarch32_UBFX_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    lsb = regex_groups.get('lsb', None)
    width = regex_groups.get('width', None)
    log.debug(f'aarch32_UBFX_T1_A Rd={Rd} Rn={Rn} lsb={lsb} width={width} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];
    lsbit = core.UInt(lsb);  
    msbit = core.UInt(width) + core.UInt(lsb);
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13
    if msbit > 31:
        msbit = 31;

    def aarch32_UBFX_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            core.R[d] = core.ZeroExtendSubField(core.R[n], msbit, lsbit, 32);
        else:
            log.debug(f'aarch32_UBFX_T1_A_exec skipped')
    return aarch32_UBFX_T1_A_exec


patterns = {
    'UBFX': [
        (re.compile(r'^UBFX(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s#(?P<lsb>\d+),\s#(?P<width>\d+)$', re.I), aarch32_UBFX_T1_A, {}),
    ],
}
