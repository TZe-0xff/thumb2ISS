import re, logging

log = logging.getLogger('Mnem.ADR')
# instruction aarch32_ADR_A
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
def aarch32_ADR_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_ADR_T1_A Rd={Rd} abs_address={hex(abs_address)} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;

    def aarch32_ADR_T1_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
        else:
            log.debug(f'aarch32_ADR_T1_A_exec skipped')
    return aarch32_ADR_T1_A_exec

# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
def aarch32_ADR_T2_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_ADR_T2_A Rd={Rd} abs_address={hex(abs_address)} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = False;
    if d == 15:
        raise Exception('UNPREDICTABLE');     # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T2_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
        else:
            log.debug(f'aarch32_ADR_T2_A_exec skipped')
    return aarch32_ADR_T2_A_exec

# pattern ADR{<c>}.W <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
# pattern ADR{<c>}{<q>} <Rd>, <label> with bitdiffs=[]
# regex ^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : c Rd abs_address
def aarch32_ADR_T3_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    cond = regex_groups.get('c', None)
    Rd = regex_groups.get('Rd', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    log.debug(f'aarch32_ADR_T3_A Rd={Rd} abs_address={hex(abs_address)} cond={cond}')
    # decode
    d = core.reg_num[Rd];  add = True;
    if d == 15:
        raise Exception('UNPREDICTABLE');   # Armv8-A removes raise Exception('UNPREDICTABLE') for R13

    def aarch32_ADR_T3_A_exec():
        # execute
        if core.ConditionPassed(cond):
            result = (core.Align(core.PC,4) + imm32) if add else (core.Align(core.PC,4) - imm32);
            if d == 15:
                          # Can only occur for A32 encodings
                core.ALUWritePC(result);
            else:
                core.R[d] = result; log.info(f'Setting R{d}={hex(core.UInt(result))}')
        else:
            log.debug(f'aarch32_ADR_T3_A_exec skipped')
    return aarch32_ADR_T3_A_exec


patterns = {
    'ADR': [
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T1_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T2_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?.W\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
        (re.compile(r'^ADR(?P<c>[ACEGHLMNPV][CEILQST])?(?:\.[NW])?\s(?P<Rd>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_ADR_T3_A, {}),
    ],
}
