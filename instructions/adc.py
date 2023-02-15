import re, logging

log = logging.getLogger('Mnem.ADC')
#pattern ADC{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '0')]
#ADC(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)
#pattern ADCS{<c>}{<q>} {<Rd>,} <Rn>, #<const> with bitdiffs=[('S', '1')]
#ADCS(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)
def aarch32_ADC_i_T1_A(core, regex_match, bitdiffs):

    # decode
    Rd = regex_match.group('Rd')
    Rn = regex_match.group('Rn')
    cond = regex_match.group('c')
    imm32 = regex_match.group('imm32')
    S = bitdiffs.get('S', '0')
    if Rd is None:
        Rd = Rn
    log.debug(f'aarch32_ADC_i_T1_A {Rd}, {Rn}, #{imm32}, setflags={S}')

    d = core.reg_num[Rd]; n = core.reg_num[Rn]; setflags = (S == '1')

    def aarch32_ADC_i_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            (result, nzcv) = core.AddWithCarry(core.R[n], imm32, core.APSR.C);
            if d == 15:          # Can only occur for A32 encoding
                if setflags:
                    raise Exception(f'ALUExceptionReturn({result})')
                else:
                    core.ALUWritePC(result);
            else:
                log.info(f'Setting R{d}={hex(core.UInt(result))}')
                core.R[d] = result
                if setflags:
                    core.APSR.update(nzcv)
        else:
            log.debug(f'aarch32_ADC_i_T1_A_exec skipped')
    return aarch32_ADC_i_T1_A_exec


patterns = {
            'ADC' : [
                (re.compile(r'^ADC(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_ADC_i_T1_A, {'S':'0'}),
                ],
            'ADCS' : [
                (re.compile(r'^ADCS(?P<c>\w\w)?(?:\.[NW])?\s(?:(?P<Rd>\w+),\s)?(?P<Rn>\w+),\s#(?P<imm32>[+-]?\d+)$', re.I), aarch32_ADC_i_T1_A, {'S':'1'}),
                ],
}


if __name__ == '__main__':
    from _testing import Core, test
    logging.basicConfig(level=logging.DEBUG)
    c = Core()

    steps = []
    steps += [c.getExec('adc', 'r0, #10', 0)]
    steps += [c.getExec('adcs', 'r1, r0, #-10', 0)]
    steps += [c.getExec('adcs', 'r1, #1', 0)]

    test(c, steps)