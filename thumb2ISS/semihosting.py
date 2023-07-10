#
# Copyright (c) 2023 Thibaut Zeissloff.
#
# This file is part of Thumb2ISS
# (see https://github.com/TZe-0xff/thumb2ISS).
#
# License: 3-clause BSD, see https://opensource.org/licenses/BSD-3-Clause
#
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


# byte 0: SHFB_MAGIC_0 0x53
# byte 1: SHFB_MAGIC_1 0x48
# byte 2: SHFB_MAGIC_2 0x46
# byte 3: SHFB_MAGIC_3 0x42
# byte 4: feature bits

FEATURE_DATA = b'SHFB\x00' #[0x53, 0x48, 0x46, 0x42, 0]

opening_mode = ['r', 'rb', 'r+', 'rb+', 'w', 'wb', 'w+', 'wb+', 'a', 'ab', 'a+', 'ab+']

standard_io = ':tt'
sm_features = ':semihosting-features'
feature_pos = 0

sh_handles = {}


def readFromMemory(core, address, size):
    byte_seq = b''.join(core.memory[i] for i in range(address, address + size))
    return byte_seq

def writeToMemory(core, data, address, size):
    for i in range(size):
        core.memory[address + i] = data[i:i+1]

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

def writeString(core, src, pointer, cnt):
    address = core.UInt(pointer)
    writeToMemory(core, src, address, cnt)



def ExecuteCmd(core):
    global feature_pos
    cmd = core.UInt(core.R[0])

    log.debug(f'Executing {hex(cmd)} semihosting command')

    if cmd == SYS_EXIT and core.UInt(core.R[1]) == 0x20026:
        core.Exit()
    if cmd == SYS_OPEN:
        str_p, mode, str_l = loadParameters(core, core.R[1])
        filename = readString(core, str_p, str_l)

        if filename == standard_io:
            file_handle = sys.stdout if mode == opening_mode.index('w') else sys.stdin
        elif filename == sm_features:
            file_handle = 'features'
            feature_pos = 0
        else:
            file_handle = open(filename, opening_mode[mode])

        sh_handles[1+len(sh_handles)] = file_handle
        core.R[0] = core.Field(len(sh_handles))
    elif cmd == SYS_CLOSE:
        f_h, = loadParameters(core, core.R[1], cnt=1)
        file_handle = sh_handles[f_h]
        if file_handle == 'features':
            pass
        elif file_handle is not None:
            file_handle.close()
        sh_handles[f_h] = None
        core.R[0] = core.Field(0)
    elif cmd == SYS_WRITE:
        f_h, str_p, str_l = loadParameters(core, core.R[1])
        write_content = readString(core, str_p, str_l)
        print(write_content, sep='', end='', file=sh_handles[f_h])
        core.R[0] = core.Field(0)
    elif cmd == SYS_READ:
        f_h, str_p, str_l = loadParameters(core, core.R[1])
        if sh_handles[f_h] == 'features':
            data_to_write = FEATURE_DATA[feature_pos:feature_pos+str_l]
            feature_pos += len(data_to_write)
            writeString(core, data_to_write, str_p, len(data_to_write))
            core.R[0] = core.Field(len(FEATURE_DATA)-feature_pos)
        else:
            raise Exception(f'Read command not implemented on regular streams')
    elif cmd == SYS_FLEN:
        f_h, = loadParameters(core, core.R[1], cnt=1)
        if sh_handles[f_h] == 'features':
            core.R[0] = core.Field(len(FEATURE_DATA))
        elif sh_handles[f_h] in [sys.stdin, sys.stdout]:
            core.R[0] = core.Field(0)
        else:
            print(sh_handles)
            raise Exception(f'Flen command not implemented on regular streams')
    elif cmd == SYS_ISTTY:
        f_h, = loadParameters(core, core.R[1], cnt=1)
        if sh_handles[f_h] in [sys.stdin, sys.stdout]:
            core.R[0] = core.Field(1)
        else:
            core.R[0] = core.Field(0)
    elif cmd == SYS_SEEK:
        f_h, t_pos = loadParameters(core, core.R[1], cnt=2)
        if sh_handles[f_h] == 'features':
            feature_pos = t_pos
            core.R[0] = core.Field(0)
        else:
            print(sh_handles)
            raise Exception(f'Seek command not implemented on regular streams')



    else:
        raise Exception(f'Cmd not implemented : {hex(cmd)}')



