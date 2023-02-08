import re


class Architecture:
    CortexM0 = 0
    CortexM0p= 1
    CortexM3 = 2
    CortexM4 = 3
    CortexM23= 4
    CortexM33= 5


class Simulator(object):

    def __init__(self, t_arch=Architecture.CortexM4):
        self.t_arch = t_arch
        #self.timings_table = timings.load(t_arch)
        self.dis_patt = {
            # Labels
            re.compile(r'^(?P<address>[\da-f]{8}) <(?P<label>[^>]+)>:') : lambda m: self.labels[m.group('label')] = int(m.group('address'), 16),
            # code
            re.compile(r'^ +(?P<address>[\da-f]+):\t(?P<encoding>[\da-f ]{4})(?: +(?P<higWord>[\da-f]{4}))? +\t(?P<mnem>[\w.]+)\t(?P<args>[^;]+)') :
                lambda addr,encoding,mnemonic,args : self.code[int(addr, 16)] = genIsn(mnemonic, args, encoding),
            # const data
            re.compile(r'^ +(?P<address>[\da-f]+):\t(?P<value>[\da-f]{8}) +\t(?P<mnem>[\w.]+)') :
                lambda addr, value, mnemonic: genConst(self.code, int(addr, 16), value, mnemonic),
            # const table/string
            re.compile(r'^ +(?P<address>[\da-f]+):\t(?P<values>(?:[\da-f]{8} )+)') :
                lambda addr, values: genConst(self.code, int(addr, 16), values),
        }

    def load(disassembly):
        self.labels = {}
        for line in disassembly:
            for pat, action in self.dis_patt.items():
                m = pat.match(line)
                if m is not None:
                    action(m)

    return True


