import re, logging

log = logging.getLogger('Mnem.CBNZ')
# instruction aarch32_CBNZ_A
# pattern CBNZ{<q>} <Rn>, <label> with bitdiffs=[('op', '1')]
# regex ^CBNZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : Rn abs_address
# pattern CBZ{<q>} <Rn>, <label> with bitdiffs=[('op', '0')]
# regex ^CBZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$ : Rn abs_address
def aarch32_CBNZ_T1_A(core, regex_match, bitdiffs):
    regex_groups = regex_match.groupdict()
    Rn = regex_groups.get('Rn', None)
    abs_address = regex_groups.get('abs_address', None)
    abs_address = int(abs_address, 16)
    op = bitdiffs.get('op', '0')
    log.debug(f'aarch32_CBNZ_T1_A Rn={Rn} abs_address={hex(abs_address)}')
    # decode
    n = core.reg_num[Rn];  nonzero = (op == '1');

    def aarch32_CBNZ_T1_A_exec():
        # execute
        if nonzero != core.IsZero(core.R[n]):
            core.CBWritePC(abs_address);
    return aarch32_CBNZ_T1_A_exec


patterns = {
    'CBNZ': [
        (re.compile(r'^CBNZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_CBNZ_T1_A, {'op': '1'}),
    ],
    'CBZ': [
        (re.compile(r'^CBZ(?:\.[NW])?\s(?P<Rn>\w+),\s(?P<abs_address>[a-f\d]+)\s*.*$', re.I), aarch32_CBNZ_T1_A, {'op': '0'}),
    ],
}
