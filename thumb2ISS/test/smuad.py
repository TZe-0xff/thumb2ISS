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
steps += [c.getExec('smuad', 'smuad r2, r1, r0', 0)] # r2=r1L*r0L+r1H*r0H
steps += [c.getExec('smuadx', 'smuadx r3, r1, r0', 0)] # r3=r1L*r0H+r1H*r0L
steps += [c.getExec('smuadx', 'smuadx r0, r1', 0)] # r0=r0L*r1H+r0H*r1L

test(c, steps, intial_regs={0: 0x10002000, 1: 0xFFFF0001, 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0xFFFFF000)
assert(c.UInt(c.R[2]) == 0x00001000)
assert(c.UInt(c.R[3]) == 0xFFFFF000)