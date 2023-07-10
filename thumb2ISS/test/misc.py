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
steps += [c.getExec('svc', 'svc #8', 0)]
steps += [c.getExec('msr', 'msr psp, r0', 0)]
steps += [c.getExec('mrs', 'mrs r1, msp', 0)]


test(c, steps, intial_regs={0: 4 , 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 4)
assert(c.UInt(c.R[1]) == 4)
assert(c.UInt(c.SP) == 4)
