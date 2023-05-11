import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('teq', 'teq r0, #10', 0)] 
steps += [c.getExec('movne', 'movne r8, r0', 0)]

steps += [c.getExec('teq', 'teq r0, r8', 0)]
steps += [c.getExec('moveq', 'moveq r9, r0', 0)]

steps += [c.getExec('teq', 'teq r0, r8, lsl #28', 0)]
steps += [c.getExec('movmi', 'movmi r10, r0', 0)]

steps += [c.getExec('movt', 'movt r10, #57005', 0)]


test(c, steps, intial_regs={0: 0x5A , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0x5A)
assert(c.UInt(c.R[8]) == 0x5A)
assert(c.UInt(c.R[9]) == 0x5A)
assert(c.UInt(c.R[10]) == 0xDEAD005A)

assert(c.APSR.N)
