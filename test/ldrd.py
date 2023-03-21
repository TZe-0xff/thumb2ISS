from _testing import Core, test
import logging, struct
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('ldrd', 'ldrd r1, r2, [r0], #+8', 0)]
steps += [c.getExec('ldrd', 'ldrd r3, r4, [r0]', 0)]
steps += [c.getExec('ldrd', 'ldrd r5, r6, [r0, #+8]!', 0)]
steps += [c.getExec('strd', 'strd r5, r6, [r0, #+8]!', 0)]
steps += [c.getExec('ldrd', 'ldrd r7, r8, [r0]', 0)]

#initialize some memory
initial_mem = {i:struct.pack('B',i) for i in range(256)}
test(c, steps, initial_mem)

assert(c.UInt(c.R[0]) == 24)
assert(c.UInt(c.R[1]) == 0x03020100)
assert(c.UInt(c.R[2]) == 0x07060504)
assert(c.UInt(c.R[3]) == 0x0b0a0908)
assert(c.UInt(c.R[4]) == 0x0f0e0d0c)
assert(c.UInt(c.R[5]) == 0x13121110)
assert(c.UInt(c.R[6]) == 0x17161514)
assert(c.UInt(c.R[7]) == 0x13121110)
assert(c.UInt(c.R[8]) == 0x17161514)
