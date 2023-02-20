import re, logging

log = logging.getLogger('Mnem.ORNS')
# instruction aarch32_ORN_i_A
# pattern ORNS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
# regex ^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
# pattern ORN{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
# regex ^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$ : c Rd* Rn imm32
def aarch32_ORN_i_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    imm32 = regex_groups.get('imm32', None)
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ORN_i_T1_A Rd={Rd} Rn={Rn} imm32={imm32} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  setflags = (S == '1');
    carry = core.APSR.C;
    if d == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ORN_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = core.R[n] | core.NOT(imm32);
            core.R[d] = result;
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_ORN_i_T1_A_exec skipped')
    return aarch32_ORN_i_T1_A_exec


patterns = {
    'ORNS': [
        (re.compile(r'^ORNS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORN_i_T1_A, {'S': '1'}),
    ],
    'ORN': [
        (re.compile(r'^ORN(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>\d+)$', re.I), aarch32_ORN_i_T1_A, {'S': '0'}),
    ],
}
