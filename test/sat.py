import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
# SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, ASR #<amount>
steps += [c.getExec('ssat', 'ssat r2, #16, r0, asr #12', 0)] # r2 = 0xFFFF8000
# SSAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, LSL #<amount>
steps += [c.getExec('ssat', 'ssat r3, #16, r1, lsl #12', 0)] # r3 = 0x00007FFF
# USAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, ASR #<amount>
steps += [c.getExec('usat', 'usat r4, #16, r0, asr #12', 0)] # r4= 0x0
# USAT{<c>}{<q>} <Rd>, #<imm>, <Rn>, LSL #<amount>
steps += [c.getExec('usat', 'usat r5, #16, r1, lsl #12', 0)] # r5= 0x0000FFFF



test(c, steps, intial_regs={0: 0x80000000, 1: 0x8000, 13:0x20001000, 15:0})

assert(c.UInt(c.R[2]) == 0xFFFF8000)
assert(c.UInt(c.R[3]) == 0x00007FFF)
assert(c.UInt(c.R[4]) == 0x00000000)
assert(c.UInt(c.R[5]) == 0x0000FFFF)