import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('sdiv', 'sdiv r2, r1, r0', 0)] # r1= 1
steps += [c.getExec('udiv', 'udiv r3, r1, r0', 0)] # r2 = 0x80000000 


test(c, steps, intial_regs={0: 3, 1:0x80000000 , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 3)
assert(c.UInt(c.R[1]) == 0x80000000)
assert(c.UInt(c.R[2]) == 0xD5555556)
assert(c.UInt(c.R[3]) == 0x2AAAAAAA)
