import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('ssub8', 'ssub8 r2, r1, r0', 0)] # r2= r1 - r0 on each byte
steps += [c.getExec('sel',   'sel r3, r1, r0', 0)] # r3 = r1 > r0 ? r1 : r0 on each byte

steps += [c.getExec('ssub16', 'ssub16 r6, r5, r4', 0)] # r6= r5 - r4 on each halfword
steps += [c.getExec('sel',    'sel r5, r4', 0)] # r5 = r5 > r4 ? r5 : r4 on each halfword


test(c, steps, intial_regs={1: 0x10203040, 0: 0x0F222D44 , 5:0x10002000, 4:0x0FFF2002 , 13:0x20001000, 15:0})

assert(c.UInt(c.R[2]) == 0x01FE03FC)
assert(c.UInt(c.R[3]) == 0x10223044)

assert(c.UInt(c.R[6]) == 0x0001FFFE)
assert(c.UInt(c.R[5]) == 0x10002002)