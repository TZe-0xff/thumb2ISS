import re, logging

log = logging.getLogger('Mnem.PKHBT')
# instruction aarch32_PKH_A
# pattern PKHBT{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, LSL #<imm>} with bitdiffs=[('tb', '0')]
# regex ^PKHBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
# pattern PKHTB{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, ASR #<imm>} with bitdiffs=[('tb', '1')]
# regex ^PKHTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+))?$ : c Rd* Rn Rm shift_t* shift_n*
def aarch32_PKH_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    shift_n = regex_groups.get('shift_n', None)
    tb = bitdiffs.get('tb', '0')
    S = bitdiffs.get('S', '0')
    T = bitdiffs.get('T', '0')
    if Rd is None:
        Rd = Rn
    if shift_n is None:
        shift_n = '0'
    if shift_t is None:
        shift_t = 'LSL'
    log.debug(f'aarch32_PKH_T1_A Rd={Rd} Rn={Rn} Rm={Rm} shift_t={shift_t} shift_n={shift_n} cond={cond}')
    # decode
    if S == '1' or T == '1':
        raise Exception('UNDEFINED');
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  tbform = (tb == '1');
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_PKH_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            operand2 = core.Shift(core.readR(m), shift_t, shift_n, core.APSR.C);  # core.APSR.C ignored
            core.writeR(d, core.SetField(core.readR(d),15,0,core.Field(operand2,15,0) if tbform else core.Field(core.readR(n),15,0)));
            core.writeR(d, core.SetField(core.readR(d),31,16,core.Field(core.readR(n),31,16)    if tbform else core.Field(operand2,31,16)));
        else:
            log.debug(f'aarch32_PKH_T1_A_exec skipped')
    return aarch32_PKH_T1_A_exec


patterns = {
    'PKHBT': [
        (re.compile(r'^PKHBT(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>LSL)\s#(?P<shift_n>\d+))?$', re.I), aarch32_PKH_T1_A, {'tb': '0'}),
    ],
    'PKHTB': [
        (re.compile(r'^PKHTB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s(?P<Rm>\w+)(?:,\s(?P<shift_t>ASR)\s#(?P<shift_n>\d+))?$', re.I), aarch32_PKH_T1_A, {'tb': '1'}),
    ],
}
