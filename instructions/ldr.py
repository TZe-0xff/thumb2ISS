import re, logging

log = logging.getLogger('Mnem.LDR')

#pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #{+}<imm>}] with bitdiffs=
#LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:, #(?P<imm32>[+]?\d+))?\]
def aarch32_LDR_i_T1_A(core, regex_match, bitdiffs):
    # decode 
    Rt = regex_match.group('Rt')
    Rn = regex_match.group('Rn')
    cond = regex_match.group('c')
    imm32 = regex_match.group('imm32')
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDR_i_T1_A {Rt}, [{Rn}, #{imm32}]')
    t = core.reg_num[Rt]; n = core.reg_num[Rn]
    index = True; add = True; wback = False;

    def aarch32_LDR_i_T1_A_exec():
        # execute
        offset_addr = (core.R[n] + imm32) if add else (core.R[n] - imm32);
        address = offset_addr if index else core.R[n];
        data = core.ReadMemU(address,4);
        if wback : core.R[n] = offset_addr;
        if t == 15 :
            if core.Field(address,1,0) == 0:
                core.LoadWritePC(data);
            else:
                raise Exception('UNPREDICTABLE');
        else:
            core.R[t] = data;

    return aarch32_LDR_i_T1_A_exec


#pattern LDR{<c>}{<q>} <Rt>, [<Rn> {, #-<imm>}] with bitdiffs=P == 1 && U == 0 && W == 0
#LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:, #-(?P<imm32>\d+))?\]
#pattern LDR{<c>}{<q>} <Rt>, [<Rn>], #{+/-}<imm> with bitdiffs=P == 0 && W == 1
#LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)
#pattern LDR{<c>}{<q>} <Rt>, [<Rn>, #{+/-}<imm>]! with bitdiffs=P == 1 && W == 1
#LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!
def aarch32_LDR_i_T4_A(core, regex_match, bitdiffs):
    # decode 
    Rt = regex_match.group('Rt')
    Rn = regex_match.group('Rn')
    cond = regex_match.group('c')
    imm32 = regex_match.group('imm32')
    P = bitdiffs.get('P', '0')
    W = bitdiffs.get('W', '0')
    U = bitdiffs.get('U', '1')
    if imm32 is None:
        imm32 = '0'
    log.debug(f'aarch32_LDR_i_T4_A {Rt}, [{Rn}, #{imm32}] ({bitdiffs})')
    t = core.reg_num[Rt]; n = core.reg_num[Rn]
    index = (P == '1'); add = (U == '1'); wback = (W == '1');

    def aarch32_LDR_i_T4_A_exec():
        # execute
        offset_addr = (core.R[n] + imm32) if add else (core.R[n] - imm32);
        address = offset_addr if index else core.R[n];
        data = core.ReadMemU(address,4);
        if wback : core.R[n] = offset_addr;
        if t == 15 :
            if core.Field(address,1,0) == 0:
                core.LoadWritePC(data);
            else:
                raise Exception('UNPREDICTABLE');
        else:
            core.R[t] = data;

    return aarch32_LDR_i_T4_A_exec


#pattern LDR{<c>}.W <Rt>, <label> with bitdiffs=[]
#pattern LDR{<c>}{<q>} <Rt>, <label> with bitdiffs=[]
#pattern LDR{<c>}{<q>} <Rt>, [PC, #{+/-}<imm>] with bitdiffs=[]
#LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC, #(?P<imm32>[+-]?\d+))?\]
def aarch32_LDR_l_T2_A(core, regex_match, bitdiffs):
    # decode
    Rt = regex_match.group('Rt')
    cond = regex_match.group('c')
    imm32 = regex_match.group('imm32')
    U = bitdiffs.get('U', '1')
    
    log.debug(f'aarch32_LDR_l_T2_A {Rt}, [PC, #{imm32}]')

    t = core.reg_num[Rt];  add = (U == '1');

    def aarch32_LDR_l_T2_A_exec():
        # execute
        base = core.Align(core.PC,4);
        address = (base + imm32) if add else (base - imm32);
        data = core.ReadMemU(address,4);
        if t == 15 :
            if core.Field(address,1,0) == 0:
                pass #core.LoadWritePC(data);
            else:
                raise Exception('UNPREDICTABLE');
        else:
            core.R[t] = data;

    return aarch32_LDR_l_T2_A_exec


patterns = {
    'LDR' : [
        (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[PC, #(?P<imm32>[+-]?\d+)\]$', re.I), aarch32_LDR_l_T2_A, {}),
        (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#(?P<imm32>[+]?\d+))?\]$', re.I), aarch32_LDR_i_T1_A, {}),
        (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)(?:,\s#-(?P<imm32>\d+))?\]$', re.I), aarch32_LDR_i_T4_A, {'P':'1','U':'0','W':'0'}),
        (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+)\],\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_LDR_i_T4_A, {'P':'0','W':'1'}),
        (re.compile(r'^LDR(?P<c>\w\w)?(?:\.[NW])?\s(?P<Rt>\w+),\s\[(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)\]!$', re.I), aarch32_LDR_i_T4_A, {'P':'1','W':'1'}),
    ]
}


if __name__ == '__main__':
    from _testing import Core, test
    import struct
    logging.basicConfig(level=logging.DEBUG)
    c = Core()

    steps = []
    steps += [c.getExec('ldr', 'r5, [pc, #28]', 0)]
    steps += [c.getExec('ldr', 'r4, [r4]', 0)]
    steps += [c.getExec('ldr', 'r3, [r1, #+1]!', 0)]
    steps += [c.getExec('ldr', 'r3, [r1, #-1]', 0)]
    steps += [c.getExec('ldr', 'r2, [r1], #+3', 0)]

    #initialize some memory
    initial_mem = {i:struct.pack('B',i) for i in range(256)}
    test(c, steps, initial_mem)