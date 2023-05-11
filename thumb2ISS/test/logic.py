import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []

# AND{<c>}{<q>} {<Rd>,} <Rn>, #<const>
steps += [c.getExec('and', 'and r1, r0, #15', 0)] # r1 = 0x0000000F
# AND{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>}
steps += [c.getExec('and', 'and r2, r0, r1, ror #4', 0)] # r2 = 0xF0000000
# AND<c>{<q>} {<Rdn>,} <Rdn>, <Rm>
steps += [c.getExec('ands', 'ands r0, r2', 0)]
steps += [c.getExec('movmi', 'movmi r3, r0', 0)]

# EOR{<c>}{<q>} {<Rd>,} <Rn>, #<const>
steps += [c.getExec('eor', 'eor r2, r1, #5', 0)] # r2 = 0x0000000A
# EOR<c>{<q>} {<Rdn>,} <Rdn>, <Rm>
steps += [c.getExec('eor', 'eor r2, r0', 0)] # r2 = 0xF000000A
# EOR{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>}
steps += [c.getExec('eors', 'eors r4, r2, r0, lsr #10', 0)] # r4 = 0xF000000A ^ 0x003C0000 = 0xF03C000A
steps += [c.getExec('movmi', 'movmi r5, r0', 0)]

# ORN{<c>}{<q>} {<Rd>,} <Rn>, #<const>
steps += [c.getExec('orn', 'orn r5, #65535', 0)] # r5 = 0xFFFF0000
# ORN{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>}
steps += [c.getExec('orns', 'orns r6, r5, r0, asr #18', 0)] # r6 = 0xFFFF0000 | ~0xFFFFFC00 = 0xFFFF0000 | 0x3FF = 0xFFFF03FF

test(c, steps, intial_regs={0: 0xFFFFFFFF, 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0xF0000000)
assert(c.UInt(c.R[1]) == 0xF)
assert(c.UInt(c.R[2]) == 0xF000000A)
assert(c.UInt(c.R[3]) == 0xF0000000)
assert(c.UInt(c.R[4]) == 0xF03C000A)
assert(c.UInt(c.R[5]) == 0xFFFF0000)
assert(c.UInt(c.R[6]) == 0xFFFF03FF)


assert(c.APSR.N)
