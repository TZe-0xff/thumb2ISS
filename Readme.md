Thumb2 ISS
===================
***ARM Thumb2 Instuction Set Simulator***


This python package implements a pure software simulator of Thumb2 instruction set, allowing to
 * execute Cortex-M targeted code (typically for Unit testing purpose)
 * debug same code (typically allowing to analyze failing tests)

It implements basic semihosting commands so that stdout can be output and end of execution detected.



Dependencies
-------
In order to parse executable ELF file, this tool relies on GCC for ARM toolchain, and especially uses `arm-none-eabi-objcopy`, `arm-none-eabi-objdump` and `arm-none-eabi-readelf` executables
Alternatively, if an intel hex file is given, this tool expects complementary files (\*.dis containing disassembly and \*.sec containing section information, format is expected to be `arm-none-eabi-objdump -d -z` and `arm-none-eabi-readelf -S` respectively)


Limitations
-------
>* _No peripheral is implemented, every memory-mapped area linked to code will be accessible as a "RAM" area_
>* _Version 0.1.0 implements Cortex-M4 instruction set (and therfore Cortex M0, Cortex M0+, Cortex-M3) but not Cortex-M4F, Cortex-M23, Cortex-M33_


Installation
-------
`pip install thumb2ISS`

*This will install required package and dependencies (click and intelhex) in python installation and provide an entry point ins python Scripts `thumb2iss`*

Usage
-------
```
Usage: thumb2ISS [OPTIONS] ELF_FILE

  Runs ELF_FILE on thumb2 Instruction Set Simulator

Options:
  -d, --debug                     Launch with debugger CLI
  -c, --cpu [M0|M0+|M3|M4|M23|M33]
                                  Tune target (cycle counting)
  -l, --log FILENAME              Full debug log in target file
  -v, --verbose                   Tune stderr output verbosity
  -t, --timeout INTEGER           Simulation timeout (s) (not applicable on
                                  debugger)  [default: 10]
  -p, --profile                   Extract statistics about instruction
                                  coverage
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```


**Simulator**
Simply pass target elf (or hex file) to `thumb2iss` executable
```bash
> thumb2iss hello_world-cm4.out

[stdout]
hello, world

[stderr]
INFO:thumb2ISS:Loaded timings for Cortex M4
INFO:thumb2ISS:Loading elf hello_world-cm4.out ...
Memory range : 0x0 - 0x3013
Memory range : 0x20000000 - 0x2000092f
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
WARNING:thumb2ISS.Sim.Core:Unsupported pld executed as NOP
hello, world
INFO:thumb2ISS:Simulation ended by end of execution (6712 cycles simulated in 0.099 s)

```

**Debugger**
Add -d to command line, you will enter an interactive command line mode with disassembly and registers view
`> thumb2iss hello_world-cm4.out -d`

```
0000005e :     ldr r0, [pc, #8]
00000060 :     bl 458 <puts>
00000064 :     movs r0, #0
00000066 :     pop {r3, pc}
00000068 :     #000029e0
reset_handler:
0000006c :   > ldr r1, [pc, #24]
0000006e :     ldr r2, [pc, #28]
00000070 :     ldr r3, [pc, #28]
00000072 :     cmp r2, r3
00000074 :     ittt lt
00000076 :     ldrlt.w r0, [r1], #4
0000007a :     strlt.w r0, [r2], #4
0000007e :     blt.n 72 <reset_handler+0x6>
00000080 :     bl 44 <systeminit>

 --------------------------------------------------

R0 : 0x00000000    R1 : 0x00000000    R2 : 0x00000000    R3 : 0x00000000
R4 : 0x00000000    R5 : 0x00000000    R6 : 0x00000000    R7 : 0x00000000
R8 : 0x00000000    R9 : 0x00000000    R10: 0x00000000    R11: 0x00000000
R12: 0x00000000    SP : 0x20008000    LR : 0xffffffff    PC : 0x0000006c
N: 0 | Z: 0 | C: 0 | V: 0 | Q: 0 | GE: 0000
Cycles:     0 (step)    0 (total)

 __________________________________________________

. Next action: (siocurqbewmh) s
> Step over

```

Navigation is performed through a initial choice that can be seen as compact (shown above) or expanded (shown below)
```
. Next action: (siocurqbewmh) s
  --- Execution ---
  s) Step over
  i) Step into
  o) Step out
  c) Run / Continue
  u) Continue until ...
  r) Reset
  q) Quit / Exit simulation
  --- Instrumentation ---
  b) Break at ...
  e) Edit breakpoints ...
  w) Write register ...
  m) Edit memory ...
  h) Help, list all choices
```

*Breakpoints* and *Continue until* commands allow to enter either address (decimal, hexidecimal value) or symbol (with completion, see example above)
```
. Next action: Continue until ...
|_ Address or symbol: m
                        main
                        memset
                        memmove
                        memchr
                        memcpy
```

*Write Register* command allows to set a register as well as perform read-modify-write operations :
```
. Next action: Write register ...
|_ Register to write: r2|=0xF0F0
```

Motivation
--------
I was looking for a license-free simulator of ARM Cortex-M micro controller core in order to run unit tests directly on PC. Running Unit tests has usually the aim to validate a "functional" behavior and has therefore little dependency on compiler used to generate the test application.
My goal is also to test compiler behavior on specific code snippets. Therefore, I need to compile my test code "for" my micro controller but it would be handy to be able to run it on a PC rather than on a development board.
Basically, I need a tool that is able to execute Thumb2 instructions without any parallelism or any time related constraint and with a single interaction : outputting stdout. Also, it will be called for each test so I need something that doesn't take long to initialize and start executing.
This kind of simulation level is typically available as part of Debuggers shipped by major Toolchains editors (Keil, IAR ...) but subject to licensing.

Looking around, I found various things :
* ARMulator => GDB simulator : limited to ARMv6  (*had a look to see what would be the effort to contribute ... not the path I chose*)
* ARM Fast Models : feels overkill, subject to licensing
* OVPsim : tried this way, again some license is involved
* QEMU : well, feels really heavy for my need

During my research, I stumbled across [Alastair Reid MRA tools](https://github.com/alastairreid/mra_tools) : Tools to extract ARM's Machine Readable Architecture Specification where I learned that ARM released its ARMv8-A architecture specification in a machine readable format. Specifically, you have access to [**Arm A32/T32 Instruction Set Architecture**](https://developer.arm.com/downloads/-/exploration-tools) that can be further limited to Thumb encoding, and give us pseudo code for the entire instruction set.

I then reused his script to parse the XML, generate python code, build some simulation logic around and there you go !
