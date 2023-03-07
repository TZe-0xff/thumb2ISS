import os,sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import Core, Register

os.chdir('..')


# default test : no memory access, 0 in registers
def test(c, steps, initial_mem={}, intial_regs={13:0x20001000, 15:0}):
    
    for k in intial_regs:
        intial_regs[k] = c.Field(intial_regs[k])
    c.configure(intial_regs[15], intial_regs[13], initial_mem)
    for i in list(range(13))+[14]:
        if i in intial_regs:
            c.R[i] = Register(intial_regs[i])

    c.showRegisters(4)
    print('-'*20)
    for s in steps:
        s()
        c.showRegisters(4)
        print('-'*20)