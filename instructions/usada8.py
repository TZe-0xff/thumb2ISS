import re, logging

log = logging.getLogger('Mnem.USADA8')
# instruction aarch32_USADA8_A
# pattern USADA8{<c>}{<q>} <Rd>, <Rn>, <Rm>, <Ra> with bitdiffs=[]
# regex ^USADA8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$ : c Rd Rn Rm Ra
def aarch32_USADA8_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    Rn = regex_groups.get('Rn', None)
    Rm = regex_groups.get('Rm', None)
    Ra = regex_groups.get('Ra', None)
    log.debug(f'aarch32_USADA8_T1_A Rd={Rd} Rn={Rn} Rm={Rm} Ra={Ra} cond={cond}')
    # decode
    d = core.reg_num[Rd];  n = core.reg_num[Rn];  m = core.reg_num[Rm];  a = core.reg_num[Ra];
    if d == 15 or n == 15 or m == 15:
        raise Exception('UNPREDICTABLE'); # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_USADA8_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            absdiff1 = core.Abs(core.UInt(core.Field(core.R[n],7,0))   - core.UInt(core.Field(core.R[m],7,0)));
            absdiff2 = core.Abs(core.UInt(core.Field(core.R[n],15,8))  - core.UInt(core.Field(core.R[m],15,8)));
            absdiff3 = core.Abs(core.UInt(core.Field(core.R[n],23,16)) - core.UInt(core.Field(core.R[m],23,16)));
            absdiff4 = core.Abs(core.UInt(core.Field(core.R[n],31,24)) - core.UInt(core.Field(core.R[m],31,24)));
            result = core.UInt(core.R[a]) + absdiff1 + absdiff2 + absdiff3 + absdiff4;
            core.R[d] = core.Field(result,31,0);
        else:
            log.debug(f'aarch32_USADA8_T1_A_exec skipped')
    return aarch32_USADA8_T1_A_exec


patterns = {
    'USADA8': [
        (re.compile(r'^USADA8(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<Rn>\w+),\s(?P<Rm>\w+),\s(?P<Ra>\w+)$', re.I), aarch32_USADA8_T1_A, {}),
    ],
}
