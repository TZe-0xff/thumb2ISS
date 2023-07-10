from _testing import Core, setup
import logging, struct
logging.basicConfig(level=logging.DEBUG)

c = Core()

flow = [
    c.getExec('ldr', 'ldr r0, [pc, #28]', 0),
    c.getExec('mov', 'mov r1, r2', 2),
    c.getExec('ldrd', 'ldrd r0, r1, [pc, #4]', 4),
    c.getExec('smmul', 'smmul r2, r3, r4', 6),
    c.getExec('ldr', 'ldr pc, [pc]', 8)
]


initial_mem = {i:struct.pack('B',i) for i in range(256)}

setup(c, initial_mem)


for step in flow:
    base_cnt = step()
    cycle_adder, branch_penalty = c.incPC(2)
    print('step cycles', base_cnt + cycle_adder)


