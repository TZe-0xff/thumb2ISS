import logging
import struct
import sys

log = logging.getLogger('SemiHost')

SYS_OPEN     = 0x01
SYS_CLOSE    = 0x02
SYS_WRITEC   = 0x03
SYS_WRITE0   = 0x04
SYS_WRITE    = 0x05
SYS_READ     = 0x06
SYS_READC    = 0x07
SYS_ISERROR  = 0x08
SYS_ISTTY    = 0x09
SYS_SEEK     = 0x0A

SYS_FLEN     = 0x0C
SYS_TMPNAME  = 0x0D
SYS_REMOVE   = 0x0E
SYS_RENAME   = 0x0F
SYS_CLOCK    = 0x10
SYS_TIME     = 0x11
SYS_SYSTEM   = 0x12
SYS_ERRNO    = 0x13

SYS_GET_CMDLINE = 0x15
SYS_HEAPINFO    = 0x16

SYS_EXIT        = 0x18


opening_mode = ['r', 'rb', 'r+', 'rb+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+']

standard_io = ':tt'

sh_handles = {}


def readFromMemory(core, address, size):
    byte_seq = b''.join(core.memory[i] for i in range(address, address + size))
    return byte_seq

def loadParameters(core, pointer, cnt=3):
    params = []
    address = core.UInt(pointer)
    for i in range(cnt):
        params.append(struct.unpack('<L', bytes(readFromMemory(core, address, 4)))[0])
        address += 4
    return params


def readString(core, pointer, cnt):
    address = core.UInt(pointer)
    str_val = readFromMemory(core, address, cnt).decode('ascii')
    return str_val


def ExecuteCmd(core):
    cmd = core.UInt(core.R[0])

    log.debug(f'Executing {hex(cmd)} semihosting command')

    if cmd == 0x18 and core.UInt(core.R[1]) == 0x20026:
        core.Exit()
    if cmd == 0x01:
        str_p, mode, str_l = loadParameters(core, core.R[1])
        filename = readString(core, str_p, str_l)

        if filename == standard_io:
            file_handle = sys.stdout if mode == opening_mode.index('w') else sys.stdin
        else:
            file_handle = open(filename, opening_mode[mode])

        sh_handles[1+len(sh_handles)] = file_handle
        core.R[0] = core.Field(len(sh_handles))
    elif cmd == 0x05:
        f_h, str_p, str_l = loadParameters(core, core.R[1])
        write_content = readString(core, str_p, str_l)
        print(write_content, sep='', end='', file=sh_handles[f_h])
        core.R[0] = core.Field(0)



