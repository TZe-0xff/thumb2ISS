#!/usr/bin/env python3
'''
Code inspired by https://github.com/alastairreid/mra_tools under BSD 3-Clause
'''

'''
Unpack ARM instruction XML files extracting the encoding information
and ASL code within it to convert into python.
'''

import argparse
import glob
import json
import os
import re
import string
import sys
import xml.etree.cElementTree as ET
from collections import defaultdict, OrderedDict
from itertools import takewhile

include_regex = None
exclude_regex = None

assembly_subst = [
    # re?       search                                  replace
    (False,         '[',                                r'\['),
    (False,         ']',                                r'\]'),
    (False,       '{+}',                                r'[+]?'),
    (False,     '{+/-}',                                r'[+-]?'),
    (True,  re.compile(r'\{?<c>\}?'),                   r'(?P<c>[ACEGHLMNPV][CEILQST])?'),
    (False,     '{<q>}',                                r'(?:\.[NW])?'),
    (False, '{<x>{<y>{<z>}}}',                          r'(?P<mask>[ET]*)'),
    (False,    '<cond>',                                r'(?P<firstcond>\w\w)'),
    (False,   '<label>',                                r'(?P<abs_address>[a-f\d]+)\s*.*'),
    (False,  '<iflags>',                                r'(?P<iflags>[if]+)'),
    (False,  '<spec_reg>',                              r'(?P<spec_reg>\w+)'),
    (False,     '.<dt>',                                r'\.F(?P<esize>\d+)'),
    (False, '<shift> #<amount>',                        r'(?P<shift_t>[LAR][SO][LR])\s#(?P<shift_n>\d+)'),
    (False, 'LSL #<imm>',                               r'(?P<shift_t>LSL)\s#(?P<shift_n>\d+)'),
    (False, 'LSL #<amount>',                            r'(?P<shift_t>LSL)\s#(?P<shift_n>\d+)'),
    (False, 'LSR #<amount>',                            r'(?P<shift_t>LSR)\s#(?P<shift_n>\d+)'),
    (False, 'ASR #<amount>',                            r'(?P<shift_t>ASR)\s#(?P<shift_n>\d+)'),
    (False, 'ROR #<amount>',                            r'(?P<shift_t>ROR)\s#(?P<rotation>\d+)'),
    (False, 'LSL <',                                    r'(?P<shift_t>LSL)\s<'),
    (False, 'LSR <',                                    r'(?P<shift_t>LSR)\s<'),
    (False, 'ASR <',                                    r'(?P<shift_t>ASR)\s<'),
    (False, 'ROR <',                                    r'(?P<shift_t>ROR)\s<'),
    (False, '<shift> <',                                r'(?P<shift_t>[LAR][SO][LR])\s<'),
    (False, 'RRX',                                      r'(?P<shift_t>RRX)'),
    (True,  re.compile(r'^\^([LAR][SO][LR])'),          r'^(?P<shift_t>\1)'),
    (True,  re.compile(r'<([QDR]\w+)>'),                r'(?P<\1>\\w+)'),
    (True,  re.compile(r'\{(.*), ?\}\s?'),              r'|?:\1,\\s|?'),
    (True,  re.compile(r' ?\{, ?(.*)\}\s?'),            r'|?:,\\s\1|?'),
    (True,  re.compile(r'#((?:\[.*\]\?)?)<imm\d*>'),    r'#(?P<imm32>\1\\d+)'),
    (True,  re.compile(r'#-<imm\d*>'),                  r'#-(?P<imm32>\\d+)'),
    (False,  '#<const>',                                r'#(?P<imm32>\d+)'),
    (False,  '{#}<imm>',                                r'#?(?P<imm32>[xa-f\d]+)'),
    (True,  re.compile(r'\{(.*?)\}'),                   r'|?:\1|?'),
    (True,  re.compile(r'#<(\w+)>'),                    r'#(?P<\1>\\d+)'),
    (False,  '<registers>',                             r'\{(?P<registers>[^}]+)\}'),
    (False,         ' ',                                r'\s')
]

dec_subst = [
    # re?       search                                  replace
    (True, re.compile(r'([a-z]\d?) = UInt\(\w*\:?(Rd?\1[nm]?)\);'),       r'\1 = core.reg_num[\2];'), # register number extraction
    (True, re.compile(r'(if .*then SEE.*)\n'),          r''),        # SEE references removal
    (True, re.compile(r"(.*?cond == '1111'.*\n)"),      r''),        # test of impossible condition removal
    (True, re.compile(r'(\s*)(.*;) *(if .*)'),          r'\1\2\n\1\3'),     # if on new lines only
    (True, re.compile(r'(\s*)(if.*) then *([^;]+;)'),     r'\1\2:\n\1    \3'), # if then syntax conversion
    (True, re.compile(r'(if .*)then'),                  r'\1:'),     # if then syntax conversion
    (True, re.compile(r'(\w+\()'),                      r'core.\1'), # subroutine calls
    (True, re.compile(r'(.*?)//(.*)'),                  r'\1#\2'),   # comment conversion
    (True, re.compile(r'.*targetInstrSet.*\n'),         r''),
    (True, re.compile(r'= (!)?core\.InITBlock\(\)'),    r'= \1(cond is not None)'),
    (True, re.compile(r'[^;]*InITBlock\(\)[^;]*;'),     r''),
    (True, re.compile(r'.*I1 = .*\n'),                  r''),
    (True, re.compile(r'.*SYSm = .*\n'),                r''),
    (False, 'UNPREDICTABLE',                            "raise Exception('UNPREDICTABLE')"),
    (False, 'UNDEFINED',                                "raise Exception('UNDEFINED')"),
    (True, re.compile(r'registers<([^>]+)>'),            r'registers[\1]'),
    (False, 'core.BitCount(registers)',                 "registers.count('1')"),
    (True, re.compile(r'SRType_(\w\w\w)'),              r"'\1'"),
    (True, re.compile('!([^=])'),                       r'not \1'),
    (False, '||',                                       'or'),
    (False, '&&',                                       'and'),
    (False, 'PSTATE',                                   'core.APSR'),
    (False, 'EOR',                                      '^'),
    (False, 'TRUE',                                     'True'),
    (False, 'FALSE',                                    'False'),
]

exec_subst = [
    # re?       search                                  replace
    (True, re.compile(r'(\s*)if CurrentInstrSet\(\) == InstrSet_A32 then.*\n\1else', re.S), r'\1if True:'),
    (True, re.compile(r'(\s*)if BigEndian\(AccessType_GPR\) then.*\n\1else', re.S), r'\1if True:'),
    (True, re.compile(r'.*targetInstrSet.*\n'),         r''),
    (True, re.compile(r'.*next_instr_addr.*\n'),        r''),
    (True, re.compile(r'(\s*)if True:\n\1([^ ])'),      r'\1\2'),
    (True, re.compile(r'bits\((\d+)\) (\w+);'),         r'\2 = 0;'),
    (True, re.compile(r'integer (\w+);'),               r'\1 = 0;'),
    (True, re.compile(r'boolean (\w+);'),               r'\1 = False;'),
    (True, re.compile(r'if (.*?) then (.*?) else'),     r'\2 if \1 else'),  # inline if else syntax conversion
    (True, re.compile(r'(\s*)(if.*) then([^;]+;)'),     r'\1\2:\n\1    \3'), # if then syntax conversion
    (True, re.compile(r'(if.*) then'),                  r'\1:'),            # if then syntax conversion
    (True, re.compile(r'(\s*else)[^\w]*\n'),            r'\1:\n'),          # if else syntax conversion
    (True, re.compile(r'(\w+\()'),                      r'core.\1'),        # subroutine calls
    (True, re.compile(r'(for[^=]+)= +(\d+) to (\d+)'),  r'\1in range(\2,\3+1):'), # for loop syntax conversion
    (True, re.compile(r'(.*?)//(.*)'),                  r'\1#\2'),          # comment conversion
    (True, re.compile(r'Int\((R\[\w+\]):(R\[\w+\])\)'), r'Int(\2, \1)'),
    (True, re.compile(r'(R\[[^]]+\])'),                 r'core.\1' ),
    (True, re.compile(r'(Mem\w)\[([^]]+)\] = (.*?);'),  r'core.Write\1(\2, \3);' ),
    (True, re.compile(r'(Mem\w)\[([^]]+)\]'),           r'core.Read\1(\2)' ),
    (True, re.compile(r'registers<([^>]+)>'),           r'registers[\1]'),
    (True, re.compile(r'SRType_(\w\w\w)'),              r"'\1'"),
    (True, re.compile(r'BranchType_(\w+)'),             r"'\1'"),
    (True, re.compile('!([^=])'),                       r'not \1'),
    (True, re.compile(r'PSTATE\.<[^>]*?> = (\w+);'),    r'core.APSR.update(\1);'),
    (True, re.compile(r"PSTATE\.GE<(\d+)> == '1'"),     r'PSTATE.GE[\1]'),
    (False, 'PSTATE.IT<7:0> = firstcond:mask;',         'core.APSR.ITcond = firstcond; core.APSR.ITsteps = len(mask)'),
    (True, re.compile(r'(\S*[\w\[\]]+)<(\d+):(\d+)> += (.*);'), r'\1 = core.SetField(\1,\2,\3,\4);'),
    (True, re.compile(r'(\S*\w+)<(\d+)> += (.*);'),        r'\1 = core.SetBit(\1,\2,\3)'),
    (True, re.compile(r'([.\w\[\]]+)<(\d+):(\d+)>'),    r'core.Field(\1,\2,\3)'),
    (True, re.compile(r'([.\w]+)<(\d+)>'),              r'core.Bit(\1,\2)'),
    (False, 'core.BitCount(registers)',                 "registers.count('1')"),
    (False, 'core.Align(PC',                            'core.Align(core.PC'),
    (False, 'UNPREDICTABLE',                            "raise Exception('UNPREDICTABLE')"),
    (False, 'PC + imm32',                               'abs_address'),
    (False, '# Do nothing',                             'pass # Do nothing'),
    (False, '||',                                       'or'),
    (False, '&&',                                       'and'),
    (False, 'PSTATE',                                   'core.APSR'),
    (True, re.compile(r"(APSR\.[NZCVQ] = )'([01])'"),   r'\1bool(\2)'),
    (False, 'EOR',                                      '^'),
    (False, ' OR ',                                     ' | '),
    (False, 'AND',                                      '&'),
    (False, 'TRUE',                                     'True'),
    (False, 'FALSE',                                    'False'),
    (False, 'core.bits(32) UNKNOWN',                    'core.Field(0xdeadbeef)'),
    (False, 'AArch32.core',                             'core'),
    (True, re.compile(r'( +)(core\.R\[([^]]+)\] = (\w+);)'), r"\1\2 log.info(f'Setting R{\3}={hex(core.UInt(\4))}')"),
]

base_mnem = ['ADC', 'ADCS', 'ADD', 'ADDS', 'ADR', 'AND', 'ANDS', 'ASR', 'ASRS', 'B', 'BFC', 'BFI', 'BIC', 'BICS', 'BKPT', 'BL', 'BLX', 'BX', 'CBNZ', 'CBZ', 'CLREX', 'CLZ', 'CMN', 'CMP', 'CPSID', 'CPSIE', 'DMB', 'DSB', 'EOR', 'EORS', 'ISB', 'IT', 'LDM', 'LDMDB', 'LDMEA', 'LDMFD', 'LDMIA', 'LDR', 'LDRB', 'LDRBT', 'LDRD', 'LDREX', 'LDREXB', 'LDREXH', 'LDRH', 'LDRHT', 'LDRSB', 'LDRSBT', 'LDRSH', 'LDRSHT', 'LDRT', 'LSL', 'LSLS', 'LSR', 'LSRS', 'MLA', 'MLS', 'MOV', 'MOVS', 'MOVT', 'MRS', 'MSR', 'MUL', 'MULS', 'MVN', 'MVNS', 'NOP', 'ORN', 'ORNS', 'ORR', 'ORRS', 'PKHBT', 'PKHTB', 'POP', 'PUSH', 'QADD', 'QADD16', 'QADD8', 'QASX', 'QDADD', 'QDSUB', 'QSAX', 'QSUB', 'QSUB16', 'QSUB8', 'RBIT', 'REV', 'REV16', 'REVSH', 'ROR', 'RORS', 'RRX', 'RRXS', 'RSB', 'RSBS', 'SADD16', 'SADD8', 'SASX', 'SBC', 'SBCS', 'SBFX', 'SDIV', 'SEL', 'SEL', 'SEV', 'SHADD16', 'SHADD8', 'SHASX', 'SHSAX', 'SHSUB16', 'SHSUB8', 'SMLABB', 'SMLABT', 'SMLAD', 'SMLADX', 'SMLAL', 'SMLALBB', 'SMLALBT', 'SMLALD', 'SMLALDX', 'SMLALTB', 'SMLALTT', 'SMLATB', 'SMLATT', 'SMLAWB', 'SMLAWT', 'SMLSD', 'SMLSDX', 'SMLSLD', 'SMLSLDX', 'SMMLA', 'SMMLAR', 'SMMLS', 'SMMLSR', 'SMMUL', 'SMMULR', 'SMUAD', 'SMUADX', 'SMULBB', 'SMULBT', 'SMULL', 'SMULTB', 'SMULTT', 'SMULWB', 'SMULWT', 'SMUSD', 'SMUSDX', 'SSAT', 'SSAT16', 'SSAX', 'SSUB16', 'SSUB8', 'STM', 'STMDB', 'STMEA', 'STMFD', 'STMIA', 'STR', 'STRB', 'STRBT', 'STRD', 'STREX', 'STREXB', 'STREXH', 'STRH', 'STRHT', 'STRT', 'SUB', 'SUBS', 'SVC', 'SXTAB', 'SXTAB16', 'SXTAH', 'SXTB', 'SXTB16', 'SXTH', 'TBB', 'TBH', 'TEQ', 'TST', 'UADD16', 'UADD8', 'UASX', 'UBFX', 'UDIV', 'UHADD16', 'UHADD8', 'UHASX', 'UHSAX', 'UHSUB16', 'UHSUB8', 'UMAAL', 'UMLAL', 'UMULL', 'UQADD16', 'UQADD8', 'UQASX', 'UQSAX', 'UQSUB16', 'UQSUB8', 'USAD8', 'USADA8', 'USAT', 'USAT16', 'USAX', 'USUB16', 'USUB8', 'UXTAB', 'UXTAB16', 'UXTAH', 'UXTB', 'UXTB16', 'UXTH', 'WFE', 'WFI']

extended_mnem = ['ASRL', 'AUT', 'AUTG', 'BF', 'BFL', 'BFLX', 'BFX', 'BLXNS', 'BTI', 'BXAUT', 'BXNS', 'CDP', 'CDP2', 'CINC', 'CINV', 'CLRM', 'CNEG', 'CSDB', 'CSEL', 'CSET', 'CSETM', 'CSINC', 'CSINV', 'CSNEG', 'CX1', 'CX1D', 'CX2', 'CX2D', 'CX3', 'CX3D', 'DBG', 'DLS', 'DLSTP', 'ESB', 'FLDMDBX', 'FLDMIAX', 'FSTMDBX', 'FSTMIAX', 'LCTP', 'LDA', 'LDAB', 'LDAEX', 'LDAEXB', 'LDAEXH', 'LDAH', 'LDC', 'LDC2', 'LE', 'LETP', 'LSLL', 'LSRL', 'MCR', 'MCR2', 'MCRR', 'MCRR2', 'MEA', 'MRC', 'MRC2', 'MRRC', 'MRRC2', 'PAC', 'PACBTI', 'PACG', 'PLD', 'PLDW', 'PLI', 'PSSBB', 'SG', 'SORSHRL', 'SQRSHR', 'SQSHL', 'SQSHLL', 'SRSHR', 'SRSHRL', 'SSBB', 'STC', 'STC2', 'STL', 'STLB', 'STLEX', 'STLEXB', 'STLEXH', 'STLH', 'TT', 'TTA', 'TTAT', 'TTT', 'UDF', 'UQRSHL', 'UQRSHLL', 'UQSHL', 'UQSHLL', 'URSHR', 'URSHRL', 'VABAV', 'VABD', 'VABS', 'VADC', 'VADD', 'VADDLV', 'VADDV', 'VAND', 'VASD', 'VASS', 'VBIC', 'VBRSR', 'VCADD', 'VCLS', 'VCLZ', 'VCMLA', 'VCMP', 'VCMP', 'VCMPE', 'VCMUL', 'VCTP', 'VCVT', 'VCVTA', 'VCVTB', 'VCVTM', 'VCVTN', 'VCVTP', 'VCVTR', 'VCVTT', 'VCX1', 'VCX2', 'VCX3', 'VDDUP', 'VDIV', 'VDNOT', 'VDOD', 'VDSEL', 'VDST', 'VDT', 'VDUP', 'VDUSH', 'VDWDUP', 'VEOR', 'VFMA', 'VFMAS', 'VFMS', 'VFNMA', 'VFNMS', 'VHADD', 'VHCADD', 'VHSUB', 'VIDRD', 'VIDUP', 'VINS', 'VIWDUP', 'VLD2', 'VLD4', 'VLDM', 'VLDR', 'VLDRB', 'VLDRH', 'VLDRW', 'VLLDM', 'VLSTM', 'VMAX', 'VMAXA', 'VMAXAV', 'VMAXNM', 'VMAXNMA', 'VMAXNMAV', 'VMAXNMV', 'VMAXV', 'VMIN', 'VMINA', 'VMINNM', 'VMINNMA', 'VMINNMAV', 'VMINNMV', 'VMINV', 'VMLA', 'VMLADAV', 'VMLALDAV', 'VMLALV', 'VMLAS', 'VMLAV', 'VMLS', 'VMLSDAV', 'VMLSLDAV', 'VMNAV', 'VMOV', 'VMOVL', 'VMOVN', 'VMOVX', 'VMRS', 'VMSR', 'VMUL', 'VMULH', 'VMULL', 'VMVN', 'VNEG', 'VNMLA', 'VNMLS', 'VNMUL', 'VORN', 'VORR', 'VQABS', 'VQADD', 'VQDMLADH', 'VQDMLAH', 'VQDMLASH', 'VQDMLSDH', 'VQDMULH', 'VQDMULL', 'VQMOVN', 'VQMOVUN', 'VQNEG', 'VQRDMLADH', 'VQRDMLAH', 'VQRDMLASH', 'VQRDMLSDH', 'VQRDMULH', 'VQRSHL', 'VQRSHRN', 'VQRSHRUN', 'VQSHL', 'VQSHLU', 'VQSHRN', 'VQSHRUN', 'VQSUB', 'VREV16', 'VREV32', 'VREV64', 'VRHADD', 'VRINT', 'VRINTA', 'VRINTM', 'VRINTN', 'VRINTP', 'VRINTR', 'VRINTX', 'VRINTZ', 'VRMLALDAVH', 'VRMLALVH', 'VRMLSLDAVH', 'VRMULH', 'VRSHL', 'VRSHR', 'VRSHRN', 'VSBC', 'VSCCLRM', 'VSEL', 'VSELEQ', 'VSELGE', 'VSELGT', 'VSELVS', 'VSHL', 'VSHLC', 'VSHLL', 'VSHR', 'VSHRN', 'VSLI', 'VSQRT', 'VSRI', 'VST2', 'VST4', 'VSTM', 'VSTR', 'VSTRB', 'VSTRD', 'VSTRH', 'VSTRW', 'VSUB', 'WLS', 'WLSTP', 'YIELD']

excluded_mnem = ['CPSIE', 'CPSID', 'DMB', 'DSB', 'ISB', 'WFE', 'WFI', 'SEV']

excluded_encoding = ['aarch32_MRS_br_T1_AS', 'aarch32_MSR_br_T1_AS']

allowed_mnem = [b for b in base_mnem if b not in excluded_mnem]



def applyReplacement(org_str, repl_table):
    working = org_str
    for isRe, pat, new in repl_table:
        if isRe:
            working = pat.sub(new, working)
        else:
            working = working.replace(pat, new)
    return working

def BuildPattern(inpat):
    working = applyReplacement('^'+inpat+'$', assembly_subst)
    secondary_pattern = None

    if 'shift_t' in working and 'imm32' in working and 'shift_n' not in working:
        working = working.replace('imm32', 'shift_n')

    fields = re.findall(r'\(\?P<(\w+)>', working)
    if len(set(fields)) != len(fields):
        # Multiple instance of same field
        for f in ['Rdm', 'Rdn']:
            if fields.count(f) > 1:
                # trailing optional argument : make it match same as first group
                candidate = working.replace(r'|?:,\s(?P<%s>\w+)|?'%(f), r'|?:,\s(?P=%s)|?'%(f), 1)
                if candidate == working:
                    # leading optional argument, build two variants of this pattern
                    if r'|?:(?P<%s>\w+),\s|?'%(f) in working:
                        # build secondary pattern with leading argument absent
                        secondary_pattern = working.replace(r'|?:(?P<%s>\w+),\s|?'%(f), r'', 1)
                        # build main pattern with both argument present and second one matching first
                        candidate = working.replace(r'|?:(?P<%s>\w+),\s|?'%(f), r'(?P<%s>\w+),\s'%(f), 1)
                        working = candidate # force following replacement
                if candidate == working:
                    # mandatory double arguments, make trailing match same as first group
                    tokens = working.split(r'?P<%s>\w+'%(f))
                    assert(len(tokens) == 3)
                    candidate = ''.join([tokens[0],r'?P<%s>\w+'%(f),tokens[1],r'?P=%s'%(f),tokens[2]])
                working = candidate
        fields = re.findall(r'\(\?P<(\w+)>', working)

    if len(set(fields)) != len(fields):
        print('Multiple instance of same field', inpat, fields)
    opt_seq = re.findall(r'\|\?:([^|]*)\|\?', working)
    opt_fields = []
    for seq in opt_seq:
        opt_fields += re.findall(r'\(\?P<(\w+)>', seq)
    working = working.replace('|?:', '(?:')
    working = working.replace('|?', ')?')
    out_patterns = [(working, fields, opt_fields)]
    if secondary_pattern is not None:
        secondary_pattern = secondary_pattern.replace('|?:', '(?:')
        secondary_pattern = secondary_pattern.replace('|?', ')?')
        out_patterns += [(secondary_pattern, fields, opt_fields)]
    return out_patterns

########################################################################
# Tag file support
########################################################################

tags = set()
'''
Write content to a 'tag file' suppressing duplicate information
'''
def emit(f, tag, content):
    if tag not in tags: # suppress duplicate entries
        tags.add(tag)
        print('TAG:'+tag, file=f)
        print(content, file=f)


########################################################################
# Workarounds
########################################################################

# workaround: v8-A code still uses the keyword 'type' as a variable name
# change that to 'type1'
def patchTypeAsVar(x):
    return re.sub(r'([^a-zA-Z0-9_\n])type([^a-zA-Z0-9_])', r'\1type1\2', x)

########################################################################
# Classes
########################################################################

class ASL:
    '''Representation of ASL code consisting of the code, list of names it defines and list of dependencies'''

    def __init__(self, name, code, defs, deps):
        self.name = name
        self.code = code
        self.defs = defs
        self.deps = deps

    def emit(self, file, tag):
        emit(file, tag, self.code)

    def put(self, ofile, indent):
        for l in self.code.splitlines():
            print(" "*indent + l, file=ofile)

    def __str__(self):
        return "ASL{"+", ".join([self.name, str(self.defs), str(self.deps)])+"}"

    # workaround: patch all ASL code with extra dependencies
    def patchDependencies(self, chunks):
        for line in self.code.splitlines():
            l = re.split('//', line)[0]  # drop comments
            for m in re.finditer('''([a-zA-Z_]\w+(\.\w+)?\[?)''', l):
                n = m.group(1)
                if n in chunks:
                    self.deps |= {chunks[n].name}
                    self.deps |= {n}
                    # print("Adding dep", n, chunks[n].name)
        self.deps -= self.defs
        # Workaround: ProcState SP field incorrectly handled
        if self.name == "shared/functions/system/ProcState": self.deps -= {"SP", "SP.write.none"}
        if "Unpredictable_WBOVERLAPST" in self.defs: self.deps -= {"PSTATE"}

    # workaround: v8-A code still uses the keyword 'type' as a variable name
    # change that to 'type1'
    def patchTypeVar(self):
        self.code = patchTypeAsVar(self.code)

    def toPrototype(self):
        '''Strip function bodies out of ASL
           This is used when a function is cut but we still need to keep
           the function body.'''
        # build groups of lines based on whether they have matching numbers of parentheses
        groups = []
        group  = []
        parens = 0
        for l in self.code.splitlines():
            group.append(l)
            # update count of matching parentheses
            openers = len(re.findall('[([]', l))
            closers = len(re.findall('[)\]]', l))
            parens = parens + openers - closers
            if parens == 0:
                groups.append(group)
                group = []
        # crude heuristic for function bodies: starts with blank chars
        # beware: only works if the ASL block only contains functions
        lines = [ l for g in groups if not g[0].startswith("    ") for l in g ]
        # print("Generating prototype for "+self.name)
        # print("  "+"\n  ".join(lines))
        return ASL(self.name, '\n'.join(lines), self.defs, set())

# Test whether instruction encoding has a field with given name
def hasField(fields, nm):
    return any(f == nm for (_, _, f, _, _) in fields)

# Turn instruction and encoding names into identifiers
# e.g., "aarch32/UHSAX/A1_A" becomes "aarch32_UHSAX_A1_A"
# and remove dots from "LDNT1D_Z.P.BR_Contiguous"
def deslash(nm):
    return nm.replace("/instrs","").replace("/", "_").replace("-","_").replace(".","_")


def emitDecoder(dec, ofile, existing_vars, indent=0):
    # convert ASL code to python decoding paragraph
    working = dec.code

    if 'UInt(Ra)' in working and 'Ra' not in existing_vars:
        working = working.replace('UInt(Ra)', '15')
    # remove affectation of existing vars
    if 'shift_n' in existing_vars and 'shift_t' in existing_vars:
        working = re.sub(rf'\(shift_t, shift_n\) = [^;]+; ?', '', working)

    subst_var = existing_vars
    if 'imm32' in existing_vars:
        subst_var += ['imm8', 'imm16']
    if 'abs_address' in existing_vars and 'imm32' not in existing_vars:
        subst_var += ['imm32']

    if 'spec_reg' in existing_vars:
        subst_var += ['write_spsr', 'read_spsr']

    for var in subst_var:
        working = re.sub(rf'({var}) = [^;]+; *', '', working)

    if 'imm32' in existing_vars:
        working = re.sub(r'\(imm32, carry\) = T32ExpandImm_C\([^,]+, ([^)]+)\)', r'carry = \1', working)

    if 'lsb' in existing_vars and 'lsbit' in working:
        working = re.sub(r'lsbit = [^;]+', r'lsbit = UInt(lsb)', working)

    if 'width' in existing_vars and 'msbit' in working:
        working = re.sub(r'msbit = [^;]+', r'msbit = UInt(width) + UInt(lsb)', working)

    if 'op' not in existing_vars:
        working = re.sub(r'.*op == .*\n', '', working)

    if 'mask' not in existing_vars:
        working = re.sub(rf'.*mask ==.*\n', '', working)        


    working = applyReplacement(working, dec_subst)

    for line in working.splitlines():
        if len(line.strip()) > 0:
            print(' '*indent, line, sep='', file=ofile)

def emitExecute(exec, ofile, existing_vars=[], indent=0):
    working = exec.code

    # TB[HB] specific
    if 'tbb' in exec.name.lower():
        working = re.sub(r'MemU\[(.*)\]\);', r'ReadMemU(\1));', working)

    # convert ASL code to python execute paragraph
    working = applyReplacement(working, exec_subst)

    if 'abs_address' in existing_vars:
        if 'imm32' not in existing_vars:
            # remove affectation of address, already computed by disassembler
            working = re.sub(r'address = [^;]+; ?', 'address = abs_address;', working)
        else:
            # both address and imm32 may exist, test if address is already set
            working = re.sub(r'(\s*)(address = [^;]+; ?)', r'\1if abs_address is None:\n\1    \2\n\1else:\n\1    address = abs_address;', working)
    if 'imm32' in existing_vars and 'imm32' not in working:
        if 'imm16' in working:
            working = working.replace('imm16', 'imm32')
        if 'imm8' in working:
            working = working.replace('imm8', 'imm32')
    if 'Replicate' in working:
        working = re.sub(r'core.R\[(\w+)\]<(\w+):(\w+)> = core.Replicate\([^;]*', r'core.R[\1] = core.R[\1] & ~((0xffffffff >> (31 - \2 + \3)) << \3)', working)

    if 'Extend' in working:
        working = re.sub(r'Extend\(core.R\[(\w+)\]<(\w+):(\w+)>', r'ExtendSubField(core.R[\1], \2, \3', working)

    if 'write_spsr' in working:
        working = 'core.WriteSpecReg(spec_reg, core.R[n]);'
    elif 'read_spsr' in working:
        working = 'core.R[d] = core.ReadSpecReg(spec_reg);'

    # RBIT specific
    if 'rbit' in exec.name.lower():
        working = "core.R[d] = core.Field(int(f'{core.UInt(core.R[m]):032b}'[::-1],2))"

    working = re.sub(r'(\s*)core.R\[(?P<dst>\w+)\]<(?P<msbit>\w+):(?P<lsbit>\w+)> = core.R\[(?P<src>\w+)\]<\((?P=msbit)-(?P=lsbit)\):0>;', 
                     r'\1tmp_R\g<dst> = core.R[\g<dst>] & ~((0xffffffff >> (31 - \g<msbit> + \g<lsbit>)) << \g<lsbit>);\n\1core.R[\g<dst>] = tmp_R\g<dst> | (core.UInt(core.R[\g<src>]) << \g<lsbit>);',
                     working)
    for line in working.splitlines():
        if len(line.strip()) > 0:
            print(' '*indent, line, sep='', file=ofile)


default_flag_value = defaultdict(lambda : 0, {'U' : 1})

class Alias:
    def __init__(self, encs):
        self.aliases = [(patterns, aliases) for name, insn_set, fields2, dec_asl, patterns, aliases in encs]
        first_pattern = self.aliases[0][0][0]
        first_alias = self.aliases[0][1][0]
        self.name = f'{first_pattern[0]} alias of {first_alias[0]}'

        self.mnem_alias = {}
        for i in range(len(self.aliases)):
            assert(len(self.aliases[i][1]) == 1)
            base_mnem, base_handler = self.aliases[i][1][0]
            if base_handler.endswith('_RRX') or base_handler.endswith('_LSL') or base_handler.endswith('_LSR') or base_handler.endswith('_ASR') or base_handler.endswith('_ROR'):
                base_handler = base_handler[:-4]
            if 'MOVS' in base_handler:
                base_handler = base_handler.replace('MOVS', 'MOV')

            if base_handler.startswith('LDM') or base_handler.startswith('STM'):
                full_handler_name = f'disabled_{base_handler}_A'
            else:
                full_handler_name = f'aarch32_{base_handler}_A'
            
            for name, pattern, _ in self.aliases[i][0]:
                #equ_pattern_root = pattern.split(' ')[0].replace(name, base_mnem)
                #if equ_pattern_root not in self.mnem_alias:
                #    self.mnem_alias[equ_pattern_root] = []
                #self.mnem_alias[equ_pattern_root] += [(name, pattern, full_handler_name)]
                if full_handler_name not in self.mnem_alias:
                    self.mnem_alias[full_handler_name] = []
                self.mnem_alias[full_handler_name] += [(name, pattern, full_handler_name)]

    def getAliasFor(self, handler_name):
        if handler_name not in self.mnem_alias:
            return []
        return [(n,p) for n,p,fhn in self.mnem_alias[handler_name]]
    
    def getAliasFor_(self, equ_root, handler_name):
        if equ_root not in self.mnem_alias:
            return []
        alias_list = [(n,p) for n,p,fhn in self.mnem_alias[equ_root] if fhn == handler_name]
        return alias_list

    def hasAliasFor(self, equ_root, handler_name):
        if equ_root in self.mnem_alias and len(self.getAliasFor_(equ_root, handler_name)) > 0:
            return True
        return False
        

class Instruction:
    '''Representation of Instructions'''

    def __init__(self, name, encs, post, conditional, exec, mnems):
        self.name = name
        self.encs = [(name, insn_set, fields2, dec_asl, patterns) for name, insn_set, fields2, dec_asl, patterns, aliases in encs]
        self.post = post
        self.conditional = conditional
        self.exec = exec
        self.mnems = mnems
        
    def emit_python_syntax(self, ofile, aliases=[]):
        print("# instruction "+ deslash(self.name), file=ofile)
        
        all_patterns = []

        for (inm,insn_set,fields,dec,pats) in self.encs:
            if insn_set.startswith('T') and deslash(inm) not in excluded_encoding:
                all_fields = []
                all_opt_fields = []
                all_bitdiffs = []
                for mnem,pat,bitdiffs in pats:
                    print("# pattern "+ pat + " with bitdiffs=%s"%(bitdiffs), file=ofile)
                    for reg_pat, fields, opt_fields in BuildPattern(pat):
                        print("# regex "+ reg_pat + " : " + " ".join(f+('*' if f in opt_fields else '') for f in fields), file=ofile)
                        all_patterns.append((mnem, len(fields), reg_pat, deslash(inm), bitdiffs))
                        all_fields += [f for f in fields if f not in all_fields]
                        all_opt_fields += [f for f in opt_fields if f not in all_opt_fields]
                        all_bitdiffs += [b[0] for b in bitdiffs if b[0] not in all_bitdiffs]
                    # test if any alias for this decoder
                    last_mnem = pat.split(' ')[0]
                    if last_mnem.startswith('LDM'):
                        last_mnem = last_mnem.replace('{IA}','')

                for alias in aliases:
                    for alias_mnem, alias_pat in alias.getAliasFor(deslash(inm)):
                        print("# alias   "+ alias_pat, file=ofile)
                        for reg_pat, fields, opt_fields in BuildPattern(alias_pat):
                           print("# regex "+ reg_pat + " : " + " ".join(f+('*' if f in opt_fields else '') for f in fields), file=ofile)
                           all_patterns.append((alias_mnem, len(fields), reg_pat, deslash(inm), []))
                           all_fields += [f for f in fields if f not in all_fields]
                           all_opt_fields += [f for f in opt_fields if f not in all_opt_fields]
                print("def ", deslash(inm), '(core, regex_match, bitdiffs):', sep='', file=ofile)
                print("    regex_groups = regex_match.groupdict()", file=ofile)
                for f in all_fields:
                    if f == 'c':
                        print(f"    cond = regex_groups.get('c', None)", file=ofile)
                    elif f == 'registers':
                        print("    reg_list = [core.reg_num[reg.strip()] for reg in regex_groups['registers'].split(',')]", file=ofile)
                        print("    registers = ['1' if reg in reg_list else '0' for reg in range(16)]", file=ofile)
                    elif f == 'Rn' and 'registers' in all_fields:
                        print(f"    {f} = regex_groups.get('{f}', 'SP')", file=ofile)
                    else:
                        print(f"    {f} = regex_groups.get('{f}', None)", file=ofile)
                        if f == 'abs_address':
                            if 'imm32' in all_fields:
                                print("    if abs_address is not None:", file=ofile)
                                print("        abs_address = int(abs_address, 16)", file=ofile)
                            else:
                                print("    abs_address = int(abs_address, 16)", file=ofile)

                if 'c' in all_fields:
                    all_fields.remove('c')
                    all_fields.append('cond')
                for b in all_bitdiffs:
                    print(f"    {b} = bitdiffs.get('{b}', '{default_flag_value[b]}')", file=ofile)

                # look for single bits that are not decoded before use to give them default value
                for b in re.findall(r"([A-Z]) [=!]= '", dec.code):
                    if b not in all_bitdiffs:
                        print(f"    {b} = bitdiffs.get('{b}', '{default_flag_value[b]}')", file=ofile)

                if 'Rd' in all_opt_fields and 'Rn' in all_fields:
                    print('    if Rd is None:', file=ofile)
                    print('        Rd = Rn', file=ofile)

                if 'Rm' in all_opt_fields and 'Rd' in all_fields:
                    print('    if Rm is None:', file=ofile)
                    print('        Rm = Rd', file=ofile)

                if 'rbit' in mnem.lower() or 'clz' in mnem.lower():
                    print('    Rn = Rm', file=ofile)

                zero_default_fields = ['imm32', 'shift_n', 'rotation']

                for f in zero_default_fields:
                    if f in all_opt_fields:
                        print(f'    if {f} is None:', file=ofile)
                        print(f"        {f} = '0'", file=ofile)

                if 'shift_t' in all_opt_fields:
                    print('    if shift_t is None:', file=ofile)
                    print("        shift_t = 'LSL'", file=ofile)


                for f in all_opt_fields:
                    if f not in ['shift_t', 'Rd', 'Rm'] + zero_default_fields:
                        print('opt :',f, all_patterns[0][0])

                print_list = [f for f in all_fields if f != 'registers']
                if 'registers' in all_fields:
                    print_list.append('reg_list')

                debug_list = []
                for f in print_list:
                    if f == 'abs_address':
                        if 'imm32' in all_fields:
                            debug_list.append(f+'={hex('+f+') if '+f+' is not None else '+f+'}')
                        else:
                            debug_list.append(f+'={hex('+f+')}')
                    else:
                        debug_list.append(f+'={'+f+'}')
                print(f"    log.debug(f'{deslash(inm)} "+" ".join(debug_list)+"')", file=ofile)
                print("    # decode", file=ofile)
                dec.patchTypeVar()
                emitDecoder(dec, ofile, all_fields+all_bitdiffs, indent=4)
                print(file=ofile)

                exec_routine = deslash(inm)+'_exec'
                print("    def ", exec_routine, '():', sep='', file=ofile)
                indent = 8
                print(" "*indent, '# execute', sep='', file=ofile)
                if self.conditional:
                    print(" "*indent, 'if core.ConditionPassed(cond):', sep='', file=ofile)
                    indent += 4
                self.exec.patchTypeVar()
                emitExecute(self.exec, ofile, all_fields, indent)

                if self.conditional:
                    indent-=4
                    print(" "*indent, 'else:', sep='', file=ofile)
                    print(" "*(indent+4), f"log.debug(f'{exec_routine} skipped')", sep='', file=ofile)
                print(f'    return {exec_routine}', file=ofile)
                print(file=ofile)

        return all_patterns

    def __str__(self):
        encs = "["+ ", ".join([inm for (inm,_,_,_) in self.encs]) +"]"
        return "Instruction{" + ", ".join([encs, (self.post.name if self.post else "-"), self.exec.name])+", "+conditional+"}"


########################################################################
# Extracting information from XML files
########################################################################

alt_slice_syntax = False
demangle_instr = False

'''
Read pseudocode to extract ASL.
'''
def readASL(ps):
    name = ps.attrib["name"]
    name = name.replace(".txt","")
    name = name.replace("/instrs","")
    name = name.replace("/Op_","/")
    chunk = ps.find("pstext")

    # list of things defined in this chunk
    defs = { x.attrib['link'] for x in chunk.findall('anchor') }

    # extract dependencies from hyperlinks in the XML
    deps = { x.attrib['link'] for x in chunk.findall('a') if not x.text.startswith("SEE") }

    # drop impl- prefixes in links
    deps = { re.sub('(impl-\w+\.)','',x) for x in deps }
    defs = { re.sub('(impl-\w+\.)','',x) for x in defs }

    # drop file references in links
    deps = { re.sub('([^#]+#)','',x) for x in deps }

    code = ET.tostring(chunk, method="text").decode().rstrip()+"\n"

    # workaround: patch operator precedence error
    code = code.replace("= e - e MOD eltspersegment;",  "= e - (e MOD eltspersegment);")
    code = code.replace("= p - p MOD pairspersegment;", "= p - (p MOD pairspersegment);")

    if alt_slice_syntax:
        code = "\n".join(map(patchSlices, code.split('\n')))

    return ASL(name, code, defs, deps)


'''
Classic ASL syntax has a syntax ambiguity involving the use of
angles (< and >) both to delimit bitslices and as comparision
operators.
We make parsing easier by converting bitslices to use square brackets
using a set of heuristics to distinguish bitslices from comparisions.
'''
def patchSlices(x):
    reIndex = r'[0-9a-zA-Z_+*:\-()[\]., ]+'
    rePart = reIndex
    reParts = rePart+"(,"+rePart+")*"
    x = re.sub("<("+reParts+")>", r'[\1]',x)
    x = re.sub("<("+reParts+")>", r'[\1]',x)
    x = re.sub("<("+reParts+")>", r'[\1]',x)
    x = re.sub("<("+reParts+")>", r'[\1]',x)
    return x

'''
Read encoding diagrams header found in encoding index XML
'''
def readDiagram(reg):
    size = reg.attrib['form']

    fields = []
    for b in reg.findall('box'):
        wd = int(b.attrib.get('width','1'))
        hi = int(b.attrib['hibit'])
        # normalise T16 reg bit numbers
        lo = hi - wd + 1
        fields.append((lo, wd))
    return (size, fields)

def squote(s):
    return "'"+s+"'"

'''
Convert a field in a decode table such as "111" or "!= 111" or None
to a legal ASL pattern
'''
def fieldToPattern(f):
    if f:
        return "!"+squote(f[3:]) if f.startswith('!= ') else squote(f)
    else:
        return "_"

'''
Read encoding diagrams entries found in encoding index XML
'''
def readDecode(d, columns):
    values = {}
    for b in d.findall('box'):
        wd = int(b.attrib.get('width','1'))
        hi = int(b.attrib['hibit'])
        lo = hi - wd + 1
        values[lo] = fieldToPattern(b.find('c').text)
    return [ values.get(lo, "_") for (lo, _) in columns ]

def readIClass(c):
    label = c.attrib['iclass']
    allocated = c.attrib.get("unallocated", "0") == "0"
    predictable = c.attrib.get("unpredictable", "0") == "0"
    assert allocated or predictable
    # print("Reading iclass "+label+" "+str(allocated)+" "+str(unpredictable))
    return (label, allocated, predictable)

'''
'''
def readGroup(label, g):
    # print("Reading group "+label)
    diagram = readDiagram(g.find("regdiagram"))
    # print("Diagram "+str(diagram))

    children = []

    for n in g.findall('node'):
        dec = readDecode(n.find('decode'), diagram[1])
        # print("Decode "+str(dec), diagram[1])
        if 'iclass' in n.attrib:
            i = readIClass(n)
            children.append((dec, False, i))
        elif 'groupname' in n.attrib:
            nm = n.attrib['groupname']
            g = readGroup(nm, n)
            children.append((dec, True, g))
        else:
            assert False
    return (label, diagram, children)

'''
'''
def readInstrName(dir, filename, encname):
    filename = dir+"/"+filename
    xml = ET.parse(filename)
    for ic in xml.findall(".//iclass"):
        decode = ic.find("regdiagram").attrib['psname']
        for enc in ic.findall("encoding"):
            if not encname or enc.attrib['name'] == encname:
                decode = decode.replace(".txt","")
                decode = decode.replace("/instrs","")
                decode = decode.replace("-","_")
                decode = decode.replace("/","_")
                return decode
    assert False

'''
'''
def readITables(dir, root):
    classes = {}
    funcgroup = None # hack: structure of XML is not quite hierarchial
    for child in root.iter():
        if child.tag == 'funcgroupheader':
            funcgroup = child.attrib['id']
            # print("Functional Group "+funcgroup)
        elif child.tag == 'iclass_sect':
            iclass_id = child.attrib['id']
            fields = [ (b.attrib['name'], int(b.attrib['hibit']), int(b.attrib.get('width', 1))) for b in child.findall('regdiagram/box') if 'name' in b.attrib ]
            # print("Group "+funcgroup +" "+ iclass_id +' '+str(fields))
            tables = []
            for i in child.findall('instructiontable'):
                iclass = i.attrib['iclass']
                headers = [ r.text for r in i.findall('thead/tr/th') if r.attrib['class'] == 'bitfields' ]
                headers = [ patchTypeAsVar(nm) for nm in headers ] # workaround
                # print("ITable "+funcgroup +" "+ iclass +" "+str(headers))
                rows = []
                for r in i.findall('tbody/tr'):
                    patterns = [ fieldToPattern(d.text) for d in r.findall('td') if d.attrib['class'] == 'bitfield' ]
                    undef    = r.get('undef', '0') == '1'
                    unpred   = r.get('unpred', '0') == '1'
                    nop      = r.get('reserved_nop_hint', '0') == '1'
                    encname  = r.get('encname')
                    nm       = "_" if undef or unpred or nop else readInstrName(dir, r.attrib['iformfile'], encname)
                    rows.append((patterns, nm, encname, undef, unpred, nop))
                tables.append((iclass, headers, rows))
                # print(iclass, fields, headers, rows)
            assert len(tables) == 1
            # discard fields that are not used to select instruction
            # fields = [ (nm, hi, wd) for (nm, hi, wd) in fields if nm in headers ]
            fields = [ (patchTypeAsVar(nm), hi, wd) for (nm, hi, wd) in fields ] # workaround
            classes[iclass_id] = (fields, tables[0])
    return classes

'''
'''
def readDecodeFile(dir, file):
    print("Reading decoder "+file)
    root = ET.parse(file)

    iset = root.getroot().attrib['instructionset']
    groups = readGroup(iset, root.find('hierarchy'))

    classes = readITables(dir, root)

    return (groups, classes)

def ppslice(f):
    (lo, wd) = f
    return (str(lo) +" +: "+ str(wd))

def printITable(ofile, level, c):
    (fields, (ic, hdr, rows)) = c
    for (fnm, hi, wd) in fields:
        print("    "*level + "__field "+ fnm +" "+str(hi-wd+1) +" +: "+str(wd), file=ofile)
    print("    "*level +"case ("+ ", ".join(hdr) +") of", file=ofile)
    for (pats, nm, encname, undef, unpred, nop) in rows:
        nm = "__encoding "+deslash(nm)
        if encname: nm = nm + " // " +encname
        if undef: nm = "__UNALLOCATED"
        if unpred: nm = "__UNPREDICTABLE"
        if nop: nm = "__NOP"
        print("    "*(level+1) +"when ("+ ", ".join(pats) +") => "+ nm, file=ofile)
    return

def printDiagram(ofile, level, reg):
    (size, fields) = reg
    print("    "*level +"case ("+ ", ".join(map(ppslice, fields)) +") of", file=ofile)
    return

def printGroup(ofile, classes, level, root):
    (label, diagram, children) = root
    print("    "*level + "// "+label, file=ofile)
    printDiagram(ofile, level, diagram)
    for (dec, isGroup, c) in children:
        if isGroup:
            print("    "*(level+1) +"when ("+ ", ".join(dec) +") =>", file=ofile)
            printGroup(ofile, classes, level+2, c)
        else:
            (label, allocated, predictable) = c
            tag = "// "+label
            if allocated and predictable:
                (fields, (ic, hdr, rows)) = classes[label]
                print("    "*(level+1) +"when ("+ ", ".join(dec) +") => " +tag, file=ofile)
                printITable(ofile, level+2, classes[label])
            else:
                if not allocated: tag = "__UNPREDICTABLE"
                if not predictable: tag = "__UNALLOCATED"
                print("    "*(level+1) +"when ("+ ", ".join(dec) +") => " +tag, file=ofile)

    return

def printDecodeTree(ofile, groups, classes):
    print("__decode", groups[0], file=ofile)
    printGroup(ofile, classes, 1, groups)

'''
Read shared pseudocode files to extract ASL.
Result is sorted so that uses come before definitions.
'''
def readShared(files):
    asl = {}
    names = set()
    for f in files:
        xml = ET.parse(f)
        for ps in xml.findall('.//ps_section/ps'):
            r = readASL(ps)
            # workaround: patch use of type as a variable name
            r.patchTypeVar()
            # workaround: patch SCTLR[] definition
            if r.name == "aarch64/functions/sysregisters/SCTLR":
                r.code = r.code.replace("bits(32) r;", "bits(64) r;")
            # workaround: patch AArch64.CheckUnallocatedSystemAccess
            if r.name == "aarch64/functions/system/AArch64.CheckUnallocatedSystemAccess":
                r.code = r.code.replace("bits(2) op0,", "bits(2) el, bits(2) op0,")
            # workaround: patch AArch64.CheckSystemAccess
            if r.name == "aarch64/functions/system/AArch64.CheckSystemAccess":
                r.code = r.code.replace("AArch64.CheckSVESystemRegisterTraps(op0, op1, crn, crm, op2);",
                                        "AArch64.CheckSVESystemRegisterTraps(op0, op1, crn, crm, op2, read);")

            # workaround: collect type definitions
            for m in re.finditer('''(?m)^(enumeration|type)\s+(\S+)''',r.code):
                r.defs.add(m.group(2))
                names |= {m.group(2)}
            # workaround: collect variable definitions
            for m in re.finditer('''(?m)^(\S+)\s+([a-zA-Z_]\w+);''',r.code):
                if m.group(1) != "type":
                    # print("variable declaration", m[1], m[2])
                    r.defs.add(m.group(2))
                    names |= {m.group(2)}
            # workaround: collect array definitions
            for m in re.finditer('''(?m)^array\s+(\S+)\s+([a-zA-Z_]\w+)''',r.code):
                # print("array declaration", m[1], m[2])
                v = m.group(2)+"["
                r.defs.add(v)
                names |= {v}
            # workaround: collect variable accessors
            for m in re.finditer('''(?m)^(\w\S+)\s+([a-zA-Z_]\w+)\s*$''',r.code):
                # print("variable accessor", m[1], m[2])
                r.defs.add(m.group(2))
                names |= {m.group(2)}
            # workaround: collect array accessors
            for m in re.finditer('''(?m)^(\w\S+)\s+([a-zA-Z_]\w+)\[''',r.code):
                # print("array accessor", m[1], m[2])
                v = m.group(2)+"["
                r.defs.add(v)
                names |= {v}
            # workaround: add PSTATE definition/dependency
            if r.name == 'shared/functions/system/PSTATE': r.defs.add("PSTATE")
            if "PSTATE" in r.code: r.deps.add("PSTATE")

            asl[r.name] = r

    return (asl, names)


'''
Read ARM's license notice from an XML file.
Convert unicode characters to ASCII equivalents (e.g,, (C)).
Return a giant comment block containing the notice.
'''
def readNotice(xml):
    # Read proprietary notice
    notice = ['/'*72, "// Proprietary Notice"]
    for p in xml.iter('para'):
        para = ET.tostring(p, method='text').decode().rstrip()
        para = para.replace("&#8217;", "'")
        para = para.replace("&#8220;", '"')
        para = para.replace("&#8221;", '"')
        para = para.replace("&#8482;", '(TM)')
        para = para.replace("&#169;", '(C)')
        para = para.replace("&#174;", '(R)')
        lines = [ ('// '+l).rstrip() for l in para.split('\n') ]
        notice.extend(lines)
    notice.append('/'*72)
    return '\n'.join(notice)

def sanitize(name):
    new_name = ""
    for c in name:
        if c not in string.ascii_letters and c not in string.digits:
            new_name += "_"
        else:
            new_name += c
    return new_name

# remove one level of indentation from code
def indent(code):
    return [ "    " + l for l in code ]

# remove one level of indentation from code
def unindent(code):
    cs = []
    for l in code:
        if l != "" and l[0:4] != "    ":
            print("Malformed conditional code '" + l[0:4] +"'")
            assert False
        cs.append(l[4:])
    return cs

# Execute ASL code often has a header like this:
#
#     if ConditionPassed() then
#         EncodingSpecificOperations();
#
# that we need to transform into a more usable form.
# Other patterns found are:
# - declaring an enumeration before the instruction
# - inserting another line of code between the first and second lines.
#   eg "if PSTATE.EL == EL2 then UNPREDICTABLE;"
# - wrapping the entire instruction in
#    "if code[0].startswith("if CurrentInstrSet() == InstrSet_A32 then"):
#
# Return value consists of (top, cond, dec, exec):
# - additional top level declarations (of enumerations)
# - boolean: is the instruction conditional?
# - additional decode logic (to be added to start of decode ASL)
# - demangled execute logic
def demangleExecuteASL(code):
    tops = None
    conditional = False
    decode = None
    if code[0].startswith("enumeration ") and code[1] == "":
        tops = code[0]
        code = code[2:]
    if code[0].startswith("if CurrentInstrSet() == InstrSet_A32 then"):
        first = code[0]
        code = code[1:]
        mid = code.index("else")
        code1 = unindent(code[:mid])
        code2= unindent(code[mid+1:])
        (tops1, conditional1, decode1, code1) = demangleExecuteASL(code1)
        (tops2, conditional2, decode2, code2) = demangleExecuteASL(code2)
        assert tops1 == None and tops2 == None
        assert conditional1 == conditional2
        code = [first] + indent(code1) + ["else"] + indent(code2)
        ([], conditional1, "\n".join([decode1 or "", decode2 or ""]), code)

    if code[0] == "if ConditionPassed() then":
        conditional = True
        code = code[1:] # delete first line
        code = unindent(code)
    if code[0] == "bits(128) result;":
        tmp = code[0]
        code[0] = code[1]
        code[1] = tmp
    elif len(code) >= 2 and code[1] == "EncodingSpecificOperations();":
        decode = code[0]
        code = code[1:]
    if code[0].startswith("EncodingSpecificOperations();"):
        rest = code[0][29:].strip()
        if rest == "":
            code = code[1:]
        else:
            code[0] = rest
    return (tops, conditional, decode, code)

def readInstruction(xml,names,sailhack):
    execs = xml.findall(".//pstext[@section='Execute']/..")
    posts = xml.findall(".//pstext[@section='Postdecode']/..")
    assert(len(posts) <= 1)
    assert(len(execs) <= 1)
    if not execs: 
        is_alias = True
        exec = None
    else:
        is_alias = False

        exec = readASL(execs[0])
        post = readASL(posts[0]) if posts else None

        if demangle_instr:
            # demangle execute code
            code = exec.code.splitlines()
            (top, conditional, decode, execute) = demangleExecuteASL(code)
            exec.code = '\n'.join(execute)
        else:
            top = None
            conditional = False
            decode = None

        exec.patchDependencies(names)
        if post: post.patchDependencies(names)

        include_matches = include_regex is None or include_regex.search(exec.name)
        exclude_matches = exclude_regex is not None and exclude_regex.search(exec.name)
        if not include_matches or exclude_matches:
            return None


    # for each encoding, read instructions encoding, matching decode ASL and index
    mnems = []
    encs = []
    for iclass in xml.findall('.//classes/iclass'):
        encoding = iclass.find('regdiagram')
        isT16 = encoding.attrib['form'] == "16"
        insn_set = "T16" if isT16 else iclass.attrib['isa']
        fields = []
        for b in encoding.findall('box'):
            wd = int(b.attrib.get('width','1'))
            hi = int(b.attrib['hibit'])
            lo = hi - wd + 1
            nm  = b.attrib.get('name', '_') if b.attrib.get('usename', '0') == '1' else '_'
            # workaround for Sail
            if sailhack and nm == 'type': nm = 'typ'
            ignore = 'psbits' in b.attrib and b.attrib['psbits'] == 'x'*wd
            consts = ''.join([ 'x'*int(c.attrib.get('colspan','1')) if c.text is None or ignore else c.text for c in b.findall('c') ])

            # workaround: add explicit slicing to LDM/STM register_list fields
            if nm == "register_list" and wd == 13: nm = nm + "<12:0>"

            # if adjacent entries are two parts of same field, join them
            # e.g., imm8<7:1> and imm8<0> or opcode[5:2] and opcode[1:0]
            m = re.match('^(\w+)[<[]', nm)
            if m:
                nm = m.group(1)
                split = True
                if fields[-1][3] and fields[-1][2] == nm:
                    (hi1,lo1,_,_,c1) = fields.pop()
                    assert(lo1 == hi+1) # must be adjacent
                    hi = hi1
                    consts = c1+consts
            else:
                split = False

            # discard != information because it is better obtained elsewhere in spec
            if consts.startswith('!='): consts = 'x'*wd

            fields.append((hi,lo,nm,split,consts))

        # pad opcode with zeros for T16 so that all opcodes are 32 bits
        if isT16:
            fields.append((15,0,'_',False,'0'*16))
        
        # workaround: avoid use of overloaded field names
        fields2 = []
        for (hi, lo, nm, split, consts) in fields:
            if (nm in ["SP", "mask", "opcode"]
               and 'x' not in consts
               and exec is not None and exec.name not in ["aarch64/float/convert/fix", "aarch64/float/convert/int"]):
                # workaround: avoid use of overloaded field name
                nm = '_'
            fields2.append((hi,lo,nm,split,consts))

        ps_section = iclass.find('ps_section/ps')
        if ps_section:
            dec_asl = readASL(ps_section)
            if decode: dec_asl.code = decode +"\n"+ dec_asl.code
            dec_asl.patchDependencies(names)

            name = dec_asl.name if insn_set in ["T16","T32","A32"] else encoding.attrib['psname']
        else:
            dec_asl = ''
            name = encoding.attrib['psname']
        patterns = []
        aliases = []
        for encoding in iclass.findall('encoding'):
            bitdiffs = re.findall(r'(\w+) == (\d+)', encoding.attrib.get('bitdiffs', ''))

            bitdiffs = [ (k,v) for k,v in bitdiffs if not re.match(r'R[a-z]', k) ]

            for asmtemplate in encoding.findall('asmtemplate'):
                iterator = asmtemplate.itertext()
                mnem = next(iterator)
                categ = mnem.split('.')[0]

                if categ not in allowed_mnem:
                    with open('discarded.log', 'a') as f:
                        print(categ, file=f)
                    continue
                if categ not in mnems:
                    mnems.append(categ)
                patterns.append((mnem, mnem+"".join(iterator), [(k,v) for k,v in bitdiffs if 'imm' not in k]))

            if is_alias:
                # find equivalent pattern
                equivalent_to = encoding.find('equivalent_to')
                asmtemplate = equivalent_to.find('asmtemplate')
                aliases.append((asmtemplate[0].text, asmtemplate[0].attrib['href'].split('#')[1]))
        if len(patterns) > 0:
            encs.append((name, insn_set, fields2, dec_asl, patterns, aliases))
    if is_alias:
        if len(encs) > 0:
            return Alias(encs), None
        else:
            return None, None
    return (Instruction(exec.name, encs, post, conditional, exec, mnems), top)

########################################################################
# Reachability analysis
########################################################################

# Visit all nodes reachable from roots
# Returns topologically sorted list of reachable nodes
# and set of reachable nodes.
def reachable(graph, roots):
    visited = set()
    sorted = []

    def worker(seen, f):
        if f in seen:
            # print("Cyclic dependency",f)
            pass
        elif f not in visited:
            visited.add(f)
            deps = list(graph[f])
            deps.sort()
            for g in deps: worker(seen + [f], g)
            sorted.append(f)

    roots = list(roots)
    roots.sort()
    for f in roots: worker([], f)
    return (sorted, visited)

########################################################################
# Canary detection
########################################################################

# Check all paths from a function 'f' to any function in the list 'canaries'
# and report every such path.
# 'callers' is a reversed callgraph (from callees back to callers)
# Prints paths in reverse order (starting function first, root last) because that
# helps identify the common paths to the the starting function f
#
# Usage is to iterate over all canaries 'f' searching for paths that should not exist
def checkCanaries(callers, isChunk, roots, f, path):
    if f in path: # ignore recursion
        pass
    elif f in roots:
        path = [ g for g in path+[f] if not isChunk(g) ]
        print("  Canary "+" ".join(path))
    elif callers[f]:
        path = path + [f]
        for g in callers[f]:
            checkCanaries(callers, isChunk, roots, g, path)

########################################################################
# Main
########################################################################

def main():
    global alt_slice_syntax
    global include_regex
    global exclude_regex
    global demangle_instr

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verbose', '-v', help='Use verbose output',
                        action = 'count', default=1)
    parser.add_argument('--altslicesyntax', help='Convert to alternative slice syntax',
                        action='store_true', default=False)
    parser.add_argument('--demangle', help='Demangle instruction ASL',
                        action='store_true', default=True)
    parser.add_argument('--output', '-o', help='Basename for output files',
                        metavar='FILE', default='arch')
    parser.add_argument('dir', metavar='<dir>',  nargs='+',
                        help='input directories')
    parser.add_argument('--filter',  help='Optional input json file to filter definitions',
                        metavar='FILE', default=[], nargs='*')
    parser.add_argument('--include', help='Regex to select instructions by name',
                        metavar='REGEX', default=None)
    parser.add_argument('--exclude', help='Regex to exclude instructions by name',
                        metavar='REGEX', default=None)
    args = parser.parse_args()

    alt_slice_syntax = args.altslicesyntax
    if args.include is not None:
        include_regex = re.compile(args.include)
    if args.exclude is not None:
        exclude_regex = re.compile(args.exclude)
    demangle_instr   = args.demangle

    encodings = ["T16", "T32"]
    if args.verbose > 0:
        if encodings != []:
            print("Selecting encodings", ", ".join(encodings))
        else:
            print("Selecting entire architecture")

    notice = readNotice(ET.parse(os.path.join(args.dir[0], 'notice.xml')))
    (shared,names) = readShared([ f for d in args.dir for f in glob.glob(os.path.join(d, 'shared_pseudocode.xml'))])

    # reverse mapping of names back to the chunks containing them
    chunks = {}
    for a in shared.values():
        for d in a.defs:
            chunks[d] = a

    for a in shared.values():
        a.patchDependencies(chunks)

    decoder_files = [ 'encodingindex.xml', 't32_encindex.xml', 'a32_encindex.xml' ]
    decoders = [ readDecodeFile(d, f) for df in decoder_files for d in args.dir for f in glob.glob(os.path.join(d, df)) ]

    sailhack = False
    instrs = []
    aliases = []
    tops   = []
    for d in args.dir:
        for inf in glob.glob(os.path.join(d, '*.xml')):
            name = re.search(r'.*[\\/](\S+)\.xml',inf).group(1)
            if name == "onebigfile": continue
            xml = ET.parse(inf)
            (instr, top) = readInstruction(xml,chunks,sailhack)
            if top: tops.append(top)
            if instr is None: continue

            if type(instr) == Alias:
                aliases.append(instr)
                continue

            if encodings != []: # discard encodings from unwanted InsnSets
                encs = [ e for e in instr.encs if e[1] in encodings ]
                if encs == []:
                    if args.verbose > 1: print("Discarding", instr.name, encodings)
                    continue
                instr.encs = encs

            instrs.append(instr)

    # Having read everything in, decide which parts to write
    # back out again and in what order
    # print([a.name for a in aliases])

    if args.verbose > 3:
        for f in shared.values():
            print("Dependencies", f.name, "=", str(f.deps))
            print("Definitions", f.name, "=", str(f.defs))

    roots    = set()
    cuts     = set()
    canaries = set()
    for fn in args.filter:
        with open(fn, "r") as f:
            try:
                filter = json.load(f)
            except ValueError as err:
                print(err)
                sys.exit(1)
            for fun in filter['roots']:
                if fun not in chunks: print("Warning: unknown root", fun)
                roots.add(fun)
            for fun in filter['cuts']:
                if fun not in chunks: print("Warning: unknown cut", fun)
                cuts.add(fun)
            for fun in filter['canaries']:
                if fun not in chunks: print("Warning: unknown canary", fun)
                canaries.add(fun)

            # treat instrs as a list of rexexps
            patterns = [ re.compile(p) for p in filter['instructions'] ]
            instrs = [ i for i in instrs
                         if any(regex.match(i.name) for regex in patterns)
                     ]
            # print("\n".join(sorted([ i.name for i in instrs ])))
    # print("\n".join(sorted(chunks.keys())))

    # Replace all cutpoints with a stub so that we keep dependencies
    # on the argument/result types but drop the definition and any
    # dependencies on the definition.
    for x,s in shared.items():
        if any([d in cuts for d in s.defs]):
            if args.verbose > 0: print("Cutting", x)
            t = s.toPrototype()
            t.patchDependencies(chunks)
            # print("Cut", t)
            shared[x] = t

    # build bipartite graph consisting of chunk names and functions
    deps = defaultdict(set) # dependencies between functions
    for a in shared.values():
        deps[a.name] = a.deps
        for d in a.defs:
            deps[d] = {a.name}

    if args.verbose > 2:
        for f in deps: print("Dependency", f, "on", str(deps[f]))


    if encodings == [] and args.filter == []:
        # default: you get everything
        if args.verbose > 0: print("Keeping entire specification")
        roots |= { x for x in shared }
    else:
        if args.verbose > 0: print("Discarding definitions unreachable from",
                               ", ".join(encodings), " instructions")
        for i in instrs:
            for (_,_,_,dec,_) in i.encs: roots |= dec.deps
            if i.post: roots |= i.post.deps
            roots |= i.exec.deps
    (live, _) = reachable(deps, roots)

    # Check whether canaries can be reached from roots
    if canaries != set():
        if args.verbose > 0: print("Checking unreachability of", ", ".join(canaries))
        rcg = defaultdict(set) # reverse callgraph
        for f, ds in deps.items():
            for d in ds:
                rcg[d].add(f)
        for canary in canaries:
            if canary in live:
                checkCanaries(rcg, lambda x: x in shared, roots, canary, [])

    # print("Live:", " ".join(live))
    # print()
    # print("Shared", " ".join(shared.keys()))

    live_chunks = [ shared[x] for x in live if x in shared ]


    instr_by_mnem = OrderedDict()
    # grouping instructions by title mnemonic
    for i in instrs:
        if len(i.encs) > 0 and len(i.mnems) > 0:
            title_mnem = i.mnems[0].split('.')[0]
            if title_mnem.endswith('S') and title_mnem not in ['MLS', 'MRS', 'SMMLS']:
                title_mnem = title_mnem[:-1]
            if title_mnem not in instr_by_mnem:
                instr_by_mnem[title_mnem] = [i]
            else:
                instr_by_mnem[title_mnem] += [i]

    comm_file  = args.output + "_common.py"

    if args.verbose > 0: print("Writing instructions to", args.output)
    for title_mnem, i_list in instr_by_mnem.items():
        with open(args.output + title_mnem.lower() + '.py', "w") as outf:
            # header
            print(f'import re, logging\n', file=outf)
            print(f"log = logging.getLogger('Mnem.{title_mnem}')", file=outf)
            all_patterns = []
            for i in i_list:
                all_patterns += i.emit_python_syntax(outf, aliases)
                print(file=outf)

            #organize patterns per mnemonic
            org_patterns = {}
            for decode_pat in all_patterns:
                mnem = decode_pat[0].split('.')[0]
                if mnem not in org_patterns:
                    org_patterns[mnem] = []
                org_patterns[mnem].append(decode_pat)

            print('patterns = {', file=outf)
            # sort them by ascending complexity
            for mnem in org_patterns:
                print(f"    '{mnem}': [", file=outf)
                for _,_,pat,method,bitdiff in sorted(org_patterns[mnem], key=lambda decode_pat : decode_pat[1]):
                    print(" "*8, "(re.compile(r'", pat, "', re.I), ", method, ', ', dict(bitdiff), '),', sep='', file=outf)
                print("    ],", file=outf)
            print("}", file=outf)



    if args.verbose > 0: print("Writing common definitions to", comm_file)
    with open(comm_file, "w") as outf:
        print(file=outf)
        for x in live_chunks:
            emitExecute(x,outf)
        
    return

if __name__ == "__main__":
    sys.exit(main())

########################################################################
# End
########################################################################
