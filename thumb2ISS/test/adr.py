import logging
from _testing import Core, test
import struct
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('add', 'add r0, pc, #84', 0)]
steps += [c.getExec('add', 'add r1, r1, pc', 0)]

initial_mem = {i:struct.pack('B',i) for i in range(256)}
test(c, steps, initial_mem)

assert(c.UInt(c.R[0]) == 0x58)
assert(c.UInt(c.R[1]) == 4)
