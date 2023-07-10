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
steps += [c.getExec('rrxs', 'rrxs r1, r0', 0)] # r1= 1
steps += [c.getExec('rrx', 'rrx r2, r2', 0)] # r2 = 0x80000000 


test(c, steps, intial_regs={0: 3 , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 3)
assert(c.UInt(c.R[1]) == 1)
assert(c.UInt(c.R[2]) == 0x80000000)
assert(c.APSR.C)