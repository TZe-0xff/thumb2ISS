import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('rsb', 'rsb r0, #0', 0)] # r0= 0 - r0 = 1
steps += [c.getExec('rsbs', 'rsbs r1, r0, r0, LSL #8', 0)] # r1 = r0 << 8 - r0 


test(c, steps, intial_regs={0: 0xFFFFFFFF , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 1)
assert(c.UInt(c.R[1]) == 0xFF)
