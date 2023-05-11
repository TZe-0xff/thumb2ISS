import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('cmp', 'cmp r3, #9', 0)]
steps += [c.getExec('sub', 'sub.w r4, r4, #4', 0)]
steps += [c.getExec('add', 'addgt.w r0, r3, #55', 0)]


test(c, steps, intial_regs={4: 4, 13:0x20001000, 15:0})

assert(c.UInt(c.R[4]) == 0)
assert(not c.APSR.Z)
assert(c.APSR.N)
assert(not c.APSR.C)
assert(not c.APSR.V)
assert(c.UInt(c.R[0]) == 0)

