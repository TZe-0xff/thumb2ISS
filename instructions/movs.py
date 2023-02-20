import re, logging

log = logging.getLogger('Mnem.MOVS')
# instruction aarch32_MOV_rr_A
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ASR <Rs> with bitdiffs=[('op', '0100')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSL <Rs> with bitdiffs=[('op', '0010')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, LSR <Rs> with bitdiffs=[('op', '0011')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
# pattern MOV<c>{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : c Rdm shift_t Rs
# pattern MOVS{<q>} <Rdm>, <Rdm>, ROR <Rs> with bitdiffs=[('op', '0111')]
# regex ^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$ : Rdm shift_t Rs
def aarch32_MOV_rr_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rdm = regex_groups.get('Rdm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    op = bitdiffs.get('op', '0')
    log.debug(f'aarch32_MOV_rr_T1_A Rdm={Rdm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rdm];  m = core.reg_num[Rdm];  s = core.reg_num[Rs];
    setflags = not (cond is not None);  

    def aarch32_MOV_rr_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.R[s],7,0));
            (result, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            core.R[d] = result;
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T1_A_exec skipped')
    return aarch32_MOV_rr_T1_A_exec

# pattern MOVS.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : Rd Rm shift_t Rs
# pattern MOVS{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '1')]
# regex ^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV<c>.W <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
# pattern MOV{<c>}{<q>} <Rd>, <Rm>, <shift> <Rs> with bitdiffs=[('S', '0')]
# regex ^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$ : c Rd Rm shift_t Rs
def aarch32_MOV_rr_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    Rd = regex_groups.get('Rd', None)
    Rm = regex_groups.get('Rm', None)
    shift_t = regex_groups.get('shift_t', None)
    Rs = regex_groups.get('Rs', None)
    cond = regex_groups.get('c', None)
    S = bitdiffs.get('S', '0')
    log.debug(f'aarch32_MOV_rr_T2_A Rd={Rd} Rm={Rm} shift_t={shift_t} Rs={Rs} cond={cond}')
    # decode
    d = core.reg_num[Rd];  m = core.reg_num[Rm];  s = core.reg_num[Rs];
    setflags = (S == '1');  
    if d == 15 or m == 15 or s == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_MOV_rr_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            shift_n = core.UInt(core.Field(core.R[s],7,0));
            (result, carry) = core.Shift_C(core.R[m], shift_t, shift_n, core.APSR.C);
            core.R[d] = result;
            if setflags:
                core.APSR.N = core.Bit(result,31);
                core.APSR.Z = core.IsZeroBit(result);
                core.APSR.C = carry;
                # core.APSR.V unchanged
        else:
            log.debug(f'aarch32_MOV_rr_T2_A_exec skipped')
    return aarch32_MOV_rr_T2_A_exec


patterns = {
    'MOV': [
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
        (re.compile(r'^MOV(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '0'}),
    ],
    'MOVS': [
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ASR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0100'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSL)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0010'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>LSR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0011'}),
        (re.compile(r'^MOVS(?:\.[NW])?\s(?P<Rdm>\w+),\s(?P=Rdm),\s(?P<shift_t>ROR)\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T1_A, {'op': '0111'}),
        (re.compile(r'^MOVS.W\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
        (re.compile(r'^MOVS(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rm>\w+),\s(?P<shift_t>[LAR][SO][LR])\s(?P<Rs>\w+)$', re.I), aarch32_MOV_rr_T2_A, {'S': '1'}),
    ],
}
