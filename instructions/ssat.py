import re, logging

log = logging.getLogger('Mnem.SSAT')
# instruction aarch32_SSAT_A
# pattern SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, ASR #<amount> with bitdiffs=[('sh', '1')]
# regex ^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$ : c Rd imm32 Rn shift_t shift_n
# pattern SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn> {, LSL #<amount>} with bitdiffs=[('sh', '0')]
# regex ^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$ : c Rd imm32 Rn shift_t* shift_n*
def aarch32_SSAT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    imm32 = regex_groups.get('imm32', None)
    Rn = regex_groups.get('Rn', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    sh = bitdiffs.get('sh', '0')
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_SSAT_T1_A Rd={Rd} imm32={imm32} Rn={Rn} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  saturate_to = core.UInt(sat_imm)+1;
    if d == 15 or n == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_SSAT_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand = core.Shift(core.R[n], shift_t, shift_n, core.APSR.C);  # core.APSR.C ignored
            (result, sat) = core.SignedSatQ(core.SInt(operand), saturate_to);
            core.R[d] = core.SignExtend(result, 32);
            if sat:
                core.APSR.Q = bool(1);
        else:
            log.debug(f'aarch32_SSAT_T1_A_exec skipped')
    return aarch32_SSAT_T1_A_exec


patterns = {
    'SSAT': [
        (re.compile(r'^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+),\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+)$', re.I), aarch32_SSAT_T1_A, {'sh': '1'}),
        (re.compile(r'^SSAT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s#(?P<imm32>\d+),\s(?P<Rn>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$', re.I), aarch32_SSAT_T1_A, {'sh': '0'}),
    ],
}
