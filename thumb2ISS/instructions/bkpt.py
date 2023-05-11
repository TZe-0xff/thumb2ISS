import re, logging

log = logging.getLogger('Mnem.BKPT')
# instruction aarch32_BKPT_A
# pattern BKPT{<q>} {#}<imm> with bitdiffs=[]
# regex ^BKPT(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$ : imm32
def aarch32_BKPT_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    imm32 = regex_groups.get('imm32', None)
    log.debug(f'aarch32_BKPT_T1_A imm32={imm32}')
    # decode

    def aarch32_BKPT_T1_A_exec():
        # execute
        core.SoftwareBreakpoint(imm32);
    return aarch32_BKPT_T1_A_exec


patterns = {
    'BKPT': [
        (re.compile(r'^BKPT(?:\.[NW])?\s#?(?P<imm32>[xa-f\d]+)$', re.I), aarch32_BKPT_T1_A, {}),
    ],
}
