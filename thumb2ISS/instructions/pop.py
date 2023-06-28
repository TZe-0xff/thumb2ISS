import re, logging

log = logging.getLogger('Mnem.POP')
# instruction aarch32_POP_A
# pattern POP{<c>}{<q>} <registers> with bitdiffs=[]
# regex ^POP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$ : c registers
# pattern LDM{<c>}{<q>} SP!, <registers> with bitdiffs=[]
# regex ^LDM(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$ : c registers
def aarch32_POP_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    log.debug(f'aarch32_POP_T1_A cond={cond} reg_list={reg_list}')
    # decode
    UnalignedAllowed = False;
    if registers.count('1') < 1:
        raise Exception('UNPREDICTABLE');

    def aarch32_POP_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.readR(13);
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.writeR(i, core.ReadMemU(address,4) if UnalignedAllowed else core.ReadMemA(address,4));
                    address = address + 4;
            if registers[15] == '1':
                if UnalignedAllowed:
                    if core.Field(address,1,0) == '00':
                        core.LoadWritePC(core.ReadMemU(address,4));
                    else:
                        raise Exception('UNPREDICTABLE');
                else:
                    core.LoadWritePC(core.ReadMemA(address,4));
            if registers[13] == '0':
                 core.writeR(13, core.readR(13) + 4*registers.count('1'));
            if registers[13] == '1':
                 core.writeR(13, UNKNOWN = 0);
        else:
            log.debug(f'aarch32_POP_T1_A_exec skipped')
    return aarch32_POP_T1_A_exec


patterns = {
    'POP': [
        (re.compile(r'^POP(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_POP_T1_A, {}),
    ],
    'LDM': [
        (re.compile(r'^LDM(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\sSP!,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_POP_T1_A, {}),
    ],
}
