from InquirerPy import inquirer
from InquirerPy.prompts.expand import ExpandChoice
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
import re


breakpoints = {'code' : [0x12a, 0x145, 0x55579]}

addresses = list(range(0x300, 0xb00))

symbols = {
    
    "main": 0xa24,
    "sendCmd": 0x336,
}


def getBreakPoints(_):
    choices = []
    for b_type in ['code']:#, 'data']
        if len(breakpoints[b_type]) > 0:
            choices += [Separator(f'---- {b_type.title()} ----')] + [Choice(a, hex(a), True) for a in breakpoints[b_type]]
    return choices 


def run():
    print('run')

def reset():
    print('reset')

def step_in():
    print('step in')

def step_out():
    print('step out')

def step_over():
    print('step over')

def get_symbol(candidate):
    if candidate in symbols:
        return symbols[candidate]
    try:
        candidate = int(candidate,0)
    except:
        candidate = addresses[0] - 1
    if candidate in addresses:
        return candidate
    return None

def querySymbol():
    return inquirer.text(
        message="Address or symbol to stop at:",
        completer={ k:None for k in symbols },
        validate=lambda result:get_symbol(result) is not None,
        filter=get_symbol,
        amark='|_',
        qmark='|_',
        mandatory=False,
    ).execute()

def until():
    address = querySymbol()
    if address is not None:
        print(f'Temporary break at {hex(address)}')

def break_at():
    address = querySymbol()
    if address is not None:
        print(f'Code break at {hex(address)}')
        breakpoints['code'].append(address)

def show_reg():
    print('reg contents : ....')

regwrite_pat = re.compile(r'r(?P<reg_id>\d+)\s*(?P<op>[+-|&])?=\s*(?P<not>~)?(?P<imm>[\dxa-f]+)\s*', re.I)
def get_regwrite(result):
    if result is not None:
        m = regwrite_pat.match(result)
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
                print(f'r{reg_id} {op}={hex(val)}')
            return exec_regwrite
    return None

def write_reg():
    action = inquirer.text(
        message="Register to write:",
        validate=lambda result:get_regwrite(result) is not None,
        filter=get_regwrite,
        mandatory=False,
        amark='|_',
        qmark='|_',
    ).execute()
    if action is not None:
        action()

def toggle_dis():
    global disassembly
    disassembly = not disassembly
    print('Disassembly', 'On' if disassembly else 'Off')

def break_edit():
    answers = inquirer.checkbox(message='Active breakpoints', choices=getBreakPoints, mandatory=False, amark='', qmark='', enabled_symbol='x', disabled_symbol='o', pointer='>').execute()
    if answers is not None:
        breakpoints['code'] = [bk for bk in breakpoints['code'] if bk in answers]
        

main_cmd = [
    Separator('--- Execution ---'),
    ExpandChoice(key='s', name='Step over', value=step_over),
    ExpandChoice(key='i', name='Step into', value=step_in),
    ExpandChoice(key='o', name='Step out', value=step_out),
    ExpandChoice(key='c', name='Run / Continue', value=run),
    ExpandChoice(key='u', name='Continue until ...', value=until),
    ExpandChoice(key='r', name='Reset', value=reset),
    ExpandChoice(key='q', name='Quit / Exit simulation', value=False),
    Separator('--- Instrumentation ---'),
    ExpandChoice(key='b', name='Break at ...', value=break_at),
    ExpandChoice(key='e', name='Edit breakpoints ...', value=break_edit),
    ExpandChoice(key='v', name='View registers', value=show_reg),
    ExpandChoice(key='w', name='Write register ...', value=write_reg),
    ExpandChoice(key='d', name='Toggle Disassembly', value=toggle_dis),

]

disassembly = False

cmd = True
while cmd:
    cmd = inquirer.expand(message='Next action:', choices=main_cmd, qmark='.', amark='.').execute()
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