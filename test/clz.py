import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('clz', 'clz r1, r0', 0)] # r0 = 0x80000000 => r1=0
steps += [c.getExec('clz', 'clz r2, r1', 0)] # r1=0 => r2 = 32
steps += [c.getExec('clz', 'clz r3, r2', 0)] # r2 = 32 => r3 = 26

test(c, steps, intial_regs={0: 0x80000000, 1: 2, 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0x80000000)
assert(c.UInt(c.R[1]) == 0)
assert(c.UInt(c.R[2]) == 32)
assert(c.UInt(c.R[3]) == 26)