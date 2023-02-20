from _testing import Core, test
import logging, struct
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('ldr', 'ldr r5, [pc, #28]', 0)]
steps += [c.getExec('ldr', 'ldr r4, [r4]', 0)]
steps += [c.getExec('ldr', 'ldr r3, [r1, #+1]!', 0)]
steps += [c.getExec('ldr', 'ldr r3, [r1, #-1]', 0)]
steps += [c.getExec('ldr', 'ldr r2, [r1], #+3', 0)]

#initialize some memory
initial_mem = {i:struct.pack('B',i) for i in range(256)}
test(c, steps, initial_mem)
