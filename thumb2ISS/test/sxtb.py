#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
steps += [c.getExec('sxtb', 'sxtb r1, r0', 0)] # r1= 0xFFFFFFFC
steps += [c.getExec('sxtb', 'sxtb r2, r0, ror #8', 0)] # r2 = 0x00000003
steps += [c.getExec('sxtb', 'sxtb r3, r0, ror #16', 0)] # r3 = 0xFFFFFFFE
steps += [c.getExec('sxtb', 'sxtb r4, r0, ror #24', 0)] # r4 = 0x00000001 


test(c, steps, intial_regs={0: 0x01FE03FC , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0x01FE03FC)
assert(c.UInt(c.R[1]) == 0xFFFFFFFC)
assert(c.UInt(c.R[2]) == 0x00000003)
assert(c.UInt(c.R[3]) == 0xFFFFFFFE)
assert(c.UInt(c.R[4]) == 0x00000001)
