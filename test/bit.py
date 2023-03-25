import logging
from _testing import Core, test
logging.basicConfig(level=logging.DEBUG)
c = Core(profile=True)

steps = []
# BFC{<c>}{<q>} <Rd>, #<lsb>, #<width>
steps += [c.getExec('bfc', 'bfc r0, #8, #12', 0)] # r0 = 0xFFF000FF
# BFI{<c>}{<q>} <Rd>, <Rn>, #<lsb>, #<width>
steps += [c.getExec('bfi', 'bfi r0, r1, #16, #8', 0)] # r0=0xFFAD00FF
# BIC{<c>}{<q>} {<Rd>,} <Rn>, #<const>
steps += [c.getExec('bic', 'bic r2, r0, #2863311530', 0)] # r2 = 0x55050055
# BIC<c>{<q>} {<Rdn>,} <Rdn>, <Rm>
steps += [c.getExec('bic', 'bic r1, r2', 0)] # r1 = 0xDEA8
# BIC{<c>}{<q>} {<Rd>,} <Rn>, <Rm> {, <shift> #<amount>}
steps += [c.getExec('bic', 'bic r3, r1, r2, ROR #8', 0)] # r3 = 0xDAA8


test(c, steps, intial_regs={0: 0xFFFFFFFF, 1: 0xDEAD, 13:0x20001000, 15:0})

assert(c.UInt(c.R[0]) == 0xFFAD00FF)
assert(c.UInt(c.R[1]) == 0xDEA8)
assert(c.UInt(c.R[2]) == 0x55050055)
assert(c.UInt(c.R[3]) == 0xDAA8)