import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('rsb', 'rsb r0, #0', 0)] # r0= 0 - r0 = 1
steps += [c.getExec('rsbs', 'rsbs r1, r0, r0, LSL #8', 0)] # r1 = r0 << 8 - r0 
steps += [c.getExec('negs', 'negs r2, r0', 0)] # r2= -r0
steps += [c.getExec('negmi', 'negmi r3, r2', 0)] # r3= -r2
steps += [c.getExec('negpl', 'negpl r3, r1', 0)] # r3 unchanged


test(c, steps, intial_regs={0: 0xFFFFFFFF , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 1)
assert(c.UInt(c.R[1]) == 0xFF)
assert(c.UInt(c.R[2]) == 0xFFFFFFFF)
assert(c.UInt(c.R[3]) == 1)
assert(c.APSR.N)