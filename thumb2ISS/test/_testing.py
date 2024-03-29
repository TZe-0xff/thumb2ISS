#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import os,sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from thumb2ISS.core import Core, Register

os.chdir('..')


def setup(c, initial_mem={}, intial_regs={13:0x20001000, 15:0}):
    for k in intial_regs:
        intial_regs[k] = c.Field(intial_regs[k])
    c.configure(intial_regs[15], intial_regs[13], initial_mem)
    for i in list(range(13))+[14]:
        if i in intial_regs:
            c.R[i] = Register(intial_regs[i])

# default test : no memory access, 0 in registers
def test(c, steps, initial_mem={}, intial_regs={13:0x20001000, 15:0}):
    
    setup(c, initial_mem, intial_regs)

    c.showRegisters(4)
    print('-'*20)
    for s in steps:
        s()
        c.showRegisters(4)
        print('-'*20)

    if c.profile:
        print('#'*5, 'Profile', '#'*5)
        used_mnems = []
        print('Unused patterns')
        for mnem in c.matched_patterns:
            used_patterns = [(pat,cnt) for pat,cnt in c.matched_patterns[mnem].items() if cnt > 0]
            if len(used_patterns) > 0:
                used_mnems.append(mnem)
                unused_patterns = [pat for pat,cnt in c.matched_patterns[mnem].items() if cnt == 0]
                print('\n-->', mnem, f'({len(unused_patterns)}/{len(c.matched_patterns[mnem])})')
                if len(unused_patterns) > 0:
                    print('\n'.join(f'   {pat}' for pat in unused_patterns))
        print('-'*20)
        print('Unused executions')
        for mnem in used_mnems:
            possible_execs = c.exec_by_mnem[mnem]
            used_execs = [(ex,c.exec_called[ex]) for ex in possible_execs if c.exec_called[ex] > 0]
            if len(used_execs) > 0:
                unused_execs = [ex for ex in possible_execs if c.exec_called[ex] == 0]
                print('\n-->', mnem, f'({len(unused_execs)}/{len(possible_execs)})')
                if len(unused_execs) > 0:
                    print('\n'.join(f'   {ex}' for ex in unused_execs))
        
        
