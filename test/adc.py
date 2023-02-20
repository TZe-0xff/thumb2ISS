import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core()

steps = []
steps += [c.getExec('adc', 'adc r0, #10', 0)]
steps += [c.getExec('adcs', 'adcs r1, r0, #10', 0)]
steps += [c.getExec('adcs', 'adcs r1, #1', 0)]
steps += [c.getExec('adcs', 'adcs r1, r0', 0)]
steps += [c.getExec('adc', 'adc r2, r1, r0', 0)]

test(c, steps)