#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
import logging, struct
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

 # 0 	:	e8df f000 	tbb	[pc, r0]
 # 4  	:	d5280e04 	.word	0x07060504
 # 8 	:	8461ab9f 	.word	0x8461ab9f 

initial_mem = {i:struct.pack('B',i) for i in range(128)}

for add in range(8):
	test(c, [c.getExec('tbb', 'tbb [pc, r0]', 0)], initial_mem, intial_regs={0: add , 13:0x20001000, 15:0})
	assert(c.UInt(c.R[15]) == 0x4 + 2*(4+add))

initial_mem = {i:struct.pack('B',i) for i in range(128) if i%2==0}
initial_mem.update({i:b'\x00' for i in range(128) if i%2==1})

for add in range(8):
	test(c, [c.getExec('tbh', 'tbh [pc, r0, lsl #1]', 0)], initial_mem, intial_regs={0: add , 13:0x20001000, 15:0})
	assert(c.UInt(c.R[15]) == 0x4 + 2*(4+2*add))

