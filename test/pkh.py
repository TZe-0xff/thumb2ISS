import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
# BFC{<c>}{<q>} <Rd>, #<lsb>, #<width>
steps += [c.getExec('pkhtb', 'pkhtb r2, r4, r2, asr #8', 0)] # r0 = 0xFFF000FF


test(c, steps, intial_regs={2: 0xDEADBEEF, 4: 0xDEADBEEF, 13:0x20001000, 15:0})

assert(c.UInt(c.R[2]) == 0xDEADADBE)
