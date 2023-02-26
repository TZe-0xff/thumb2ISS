import re, logging

log = logging.getLogger('Mnem.LDMDB')
# instruction aarch32_LDMDB_A
# pattern LDMDB{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# pattern LDMEA{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
def aarch32_LDMDB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    W = bitdiffs.get('W', '0')
    P = bitdiffs.get('P', '0')
    M = bitdiffs.get('M', '0')
    log.debug(f'aarch32_LDMDB_T1_A Rn={Rn} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  wback = (W == '1');
    if n == 15 or registers.count('1') < 2 or (P == '1' and M == '1'):
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_LDMDB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.R[n] - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    core.R[i] = core.ReadMemS(address,4);  address = address + 4;
            if registers[15] == '1':
                core.LoadWritePC(core.ReadMemS(address,4));
            if wback and registers[n] == '0':
                 core.R[n] = core.R[n] - 4*registers.count('1');
            if wback and registers[n] == '1':
                 core.R[n] = UNKNOWN = 0;
        else:
            log.debug(f'aarch32_LDMDB_T1_A_exec skipped')
    return aarch32_LDMDB_T1_A_exec


patterns = {
    'LDMDB': [
        (re.compile(r'^LDMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
    ],
    'LDMEA': [
        (re.compile(r'^LDMEA(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_LDMDB_T1_A, {}),
    ],
}
