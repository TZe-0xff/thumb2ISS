import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('smull', 'smull r2, r3, r1, r0', 0)] # r3,r2 = r1*r0
steps += [c.getExec('smlal', 'smlal r2, r3, r1, r0', 0)] # r3,r2 = r3,r2 + r1*r0
steps += [c.getExec('smull', 'smull r4, r5, r0, r0', 0)] # r4,r5 = r0*r0

test(c, steps, intial_regs={0: 0x40000000, 1: 0x2, 2: 0xffffffff, 3: 0xffffffff, 13:0x20001000, 15:0})

assert(c.UInt(c.R[2]) == 0x00000000)
assert(c.UInt(c.R[3]) == 0x00000001)
assert(c.UInt(c.R[4]) == 0x00000000)
assert(c.UInt(c.R[5]) == 0x10000000)