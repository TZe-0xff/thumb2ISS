from _testing import Core, test
import logging, struct
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('ldr', 'ldr r5, [pc, #28]', 0)]
steps += [c.getExec('ldr', 'ldr r4, [r4]', 0)]
steps += [c.getExec('ldr', 'ldr r3, [r1, #+1]!', 0)]
steps += [c.getExec('ldr', 'ldr r2, [r1, #-1]', 0)]
steps += [c.getExec('ldr', 'ldr r0, [r1], #+3', 0)]
steps += [c.getExec('ldrsb', 'ldrsb r6, [r6, #+128]', 0)]
steps += [c.getExec('ldrsh', 'ldrsh r7, [r7, #+128]', 0)]

#initialize some memory
initial_mem = {i:struct.pack('B',i) for i in range(256)}
test(c, steps, initial_mem)

assert(c.UInt(c.R[7]) == 0xffff8180)
assert(c.UInt(c.R[6]) == 0xffffff80)
assert(c.UInt(c.R[5]) == 0x23222120)
assert(c.UInt(c.R[4]) == 0x03020100)
assert(c.UInt(c.R[3]) == 0x04030201)
assert(c.UInt(c.R[2]) == 0x03020100)
assert(c.UInt(c.R[0]) == 0x04030201)
assert(c.UInt(c.R[1]) == 4)
