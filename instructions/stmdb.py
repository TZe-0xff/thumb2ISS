import re, logging

log = logging.getLogger('Mnem.STMDB')
# instruction aarch32_STMDB_A
# pattern STMDB{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
# pattern STMFD{<c>}{<q>} <Rn>{!}, <registers> with bitdiffs=[]
# regex ^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$ : c Rn registers
def aarch32_STMDB_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rn = regex_groups.get('Rn', 'SP')
    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]
    registers = ['1' if reg in reg_list else '0' for reg in range(16)]
    W = bitdiffs.get('W', '0')
    log.debug(f'aarch32_STMDB_T1_A Rn={Rn} cond={cond} reg_list={reg_list}')
    # decode
    n = core.reg_num[Rn];  wback = (W == '1');
    if n == 15 or registers.count('1') < 2:
        raise Exception('UNPREDICTABLE');
    if wback and registers[n] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[13] == '1':
        raise Exception('UNPREDICTABLE');
    if registers[15] == '1':
        raise Exception('UNPREDICTABLE');

    def aarch32_STMDB_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            address = core.R[n] - 4*registers.count('1');
            for i in range(0,14+1):
                if registers[i] == '1':
                    if i == n and wback and i != core.LowestSetBit(registers):
                        core.WriteMemS(address,4, UNKNOWN = 0);  # Only possible for encoding A1
                    else:
                        core.WriteMemS(address,4, core.R[i]);
                    address = address + 4;
            if registers[15] == '1':
                  # Only possible for encoding A1
                core.WriteMemS(address,4, core.PCStoreValue());
            if wback:
                 core.R[n] = core.R[n] - 4*registers.count('1');
        else:
            log.debug(f'aarch32_STMDB_T1_A_exec skipped')
    return aarch32_STMDB_T1_A_exec


patterns = {
    'STMDB': [
        (re.compile(r'^STMDB(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
    ],
    'STMFD': [
        (re.compile(r'^STMFD(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rn>\w+)(?:!)?,\s\{(?P<registers>[^}]+)\}$', re.I), aarch32_STMDB_T1_A, {}),
    ],
}
