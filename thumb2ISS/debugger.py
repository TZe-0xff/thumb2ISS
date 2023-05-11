from InquirerPy import inquirer
from InquirerPy.prompts.expand import ExpandChoice
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import re, os
from .sim import Simulator, Core


class Debugger():
    def __init__(self):
        sim = Simulator()
        self.symbols = sim.getSymbols()
        self.symb_completer = { k:None for k in self.symbols }
        self.regwrite_pat = re.compile(r'r(?P<reg_id>\d+)\s*(?P<op>[+-|&])?=\s*(?P<not>~)?(?P<imm>[\dxa-f]+)\s*', re.I)
        self.main_cmd = [
        Separator('--- Execution ---'),
        ExpandChoice(key='s', name='Step over', value=self.step_over),
        ExpandChoice(key='i', name='Step into', value=self.step_in),
        ExpandChoice(key='o', name='Step out', value=self.step_out),
        ExpandChoice(key='c', name='Run / Continue', value=self.run),
        ExpandChoice(key='u', name='Continue until ...', value=self.until),
        ExpandChoice(key='r', name='Reset', value=self.reset),
        ExpandChoice(key='q', name='Quit / Exit simulation', value=False),
        Separator('--- Instrumentation ---'),
        ExpandChoice(key='b', name='Break at ...', value=self.break_at),
        ExpandChoice(key='e', name='Edit breakpoints ...', value=self.break_edit),
        ExpandChoice(key='w', name='Write register ...', value=self.write_reg),
        ExpandChoice(key='m', name='Edit memory ...', value=self.mem_edit),
    ]

    def step_over(self):
        Simulator().step_over()

    def step_in(self):
        Simulator().step_in()

    def step_out(self):
        Simulator().step_out()

    def run(self):
        Simulator().run()

    def reset(self):
        Simulator().reset()


    def until(self):
        address = self.querySymbol()
        if address is not None:
            Simulator().run_until(address)

    def break_at(self):
        address = self.querySymbol()
        if address is not None:
            Simulator().addBreakpoint(address)

    def get_symbol(self, candidate):
        if candidate in self.symbols:
            return self.symbols[candidate]
        try:
            candidate = int(candidate,0)
        except:
            candidate = -1
        if Simulator().isAddressValid(candidate):
            return candidate
        return None

    def querySymbol(self):
        return inquirer.text(
            message="Address or symbol:",
            completer=self.symb_completer,
            validate=lambda result:self.get_symbol(result) is not None,
            filter=self.get_symbol,
            amark='| ',
            qmark='|_',
            mandatory=False,
        ).execute()

    def break_edit(self):
        sim = Simulator()
        original_bkpt_list = sim.getBreakPoints()
        if len(original_bkpt_list) > 0:
            choices = [Choice(bkpt, hex(bkpt), True) for bkpt in original_bkpt_list]
            remaining_bkpt_list = inquirer.checkbox(message='Active breakpoints', choices=choices, mandatory=False, amark='', qmark=''
                #, enabled_symbol='x', disabled_symbol='o', pointer='>'
                ).execute()
            if remaining_bkpt_list is not None:
                removed_bkpt_list = [bkpt for bkpt in original_bkpt_list if bkpt not in remaining_bkpt_list]
                for bkpt in removed_bkpt_list:
                    sim.removeBreakpoint(bkpt)

    def get_value(self, candidate):
        try:
            candidate = int(candidate,0)
        except:
            candidate = None
        return candidate


    def mem_edit(self):
        sim = Simulator()
        address = self.querySymbol()
        if address is not None:
            data_size = inquirer.select(
                message="Select data size:",
                choices=[
                    Choice(value=1, name="Byte"),
                    Choice(value=2, name="Half"),
                    Choice(value=4, name="Word"),
                    Choice(value=8, name="DblWord"),
                ],
                amark='| ',
                qmark='|_',
                default=4,
                mandatory=False
            ).execute()
            if data_size is not None:
                raw_data = b''.join(sim.memory[i] for i in range(address, address+data_size))

                udata = int.from_bytes(raw_data, byteorder='little')
                ndata = inquirer.text(
                    message=f"Current val ({hex(udata)}), new val : (Ctrl-Z to cancel)",
                    validate=lambda result:self.get_value(result) is not None,
                    filter=self.get_value,
                    amark='| ',
                    qmark='|_',
                    mandatory=False,
                ).execute()
                if ndata is not None:            
                    i = 0
                    for b in ndata.to_bytes(data_size, byteorder='little'):
                        sim.memory[address+i] = b.to_bytes(1, byteorder='little')
                        i+=1

    def get_regwrite(self, result):
        if result is not None:
            m = self.regwrite_pat.match(result)
            if m is not None:
                reg_id = int(m.group('reg_id'))
                op = m.group('op')
                op = op if op is not None else ''
                try:
                    val = int(m.group('imm'), 0)
                except:
                    return None
                if m.group('not'):
                    val = ~val
                def exec_regwrite():
                    core = Core()
                    if op is None or op == '':
                        core.R[reg_id] = core.Field(val)
                    elif op == '+':
                        core.R[reg_id] = core.R[reg_id] + val
                    elif op == '-':
                        core.R[reg_id] = core.R[reg_id] - val
                    elif op == '|':
                        core.R[reg_id] = core.R[reg_id] | val
                    elif op == '&':
                        core.R[reg_id] = core.R[reg_id] & val
                return exec_regwrite
        return None

    def write_reg(self):
        action = inquirer.text(
            message="Register to write:",
            validate=lambda result:self.get_regwrite(result) is not None,
            filter=self.get_regwrite,
            mandatory=False,
            amark='|_',
            qmark='|_',
        ).execute()
        if action is not None:
            action()
            print(Core().R[1].ival, Core())
            Core().showRegisters()

    def loop(self):
        cmd = True
        sim = Simulator()
        while cmd:
            os.system('cls')
            # display disassembly
            total_lines = os.get_terminal_size().lines
            if total_lines > 12+13:
                dis_lines = total_lines - 12
                bef = -int(0.4 * dis_lines)
                aft = dis_lines + bef
            else:
                dis_lines = 15
                bef = -5
                aft = 8
            lines = sim.getDisassemblyAroundPC(bef, aft)
            lines = ['']*(dis_lines - len(lines)) + lines
            print('\n'.join(lines))
            print('\n','-'*50, '\n')
            # display registers
            regs, apsr = sim.getRegisters()
            lines = []
            cur_line = ''
            for l in range(4):
                lines.append('    '.join([f'{r}: {h}' for r,h in regs[l*4:(l+1)*4]]))
            lines.append(apsr)
            print('\n'.join(lines))
            print('\n','_'*50, '\n')
            cmd = inquirer.expand(message='Next action:', choices=self.main_cmd, qmark='.', amark='.').execute()
            if cmd:
                cmd()



# h   help
# i   step into
# s              step (over)
# o             step out
# 
# r              reset
# c              continue
# q             quit
# 
# u  <address>/<symbol>
# until <address>/<symbol>  (temporary bkpt)
# 
# b <address>/<symbol> lambda
# break <address>/<symbol> lambda
# 
# break conditional
# 
# break reg == xxx
# break read @ address
# break write @ address
# @r                                                          show registers
# 
# @rxx                                     read register
# 
# @rxx = val                           write register
# 
#  
# 
# @ address:sz     read mem
# 
# @ address:sz = val            write mem