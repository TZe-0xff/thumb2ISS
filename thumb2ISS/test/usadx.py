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
steps += [c.getExec('usad8', 'usad8 r1, r0', 0)] # r1=1+2+3+4
steps += [c.getExec('usada8', 'usada8 r4, r2, r3, r1', 0)] # r4 = r1 + 1+1+0+1

test(c, steps, intial_regs={0: 0x10203040, 1: 0x0F222D44 , 2:0xFF008080, 3:0xFE01807F , 13:0x20001000, 15:0})

assert(c.UInt(c.R[1]) == 10)
assert(c.UInt(c.R[4]) == 13)