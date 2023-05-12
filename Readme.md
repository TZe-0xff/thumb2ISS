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
  -d, --debug            Launch with debugger CLI
  -l, --log FILENAME     Full debug log in target file
  -v, --verbose          Tune stderr output verbosity
  -t, --timeout INTEGER  Simulation timeout (s) (not applicable on debugger)
                         [default: 10]
  -p, --profile          Extract statistics about instruction coverage
  --help                 Show this message and exit.
```


**Simulator**
Simply pass target elf to `thumb2iss` executable
```bash
> thumb2iss SMULDualTests.Runner.out

[stdout]
Test\SMULDualTests.c:12:test_SMUAD:PASS
Test\SMULDualTests.c:31:test_SMUADX:PASS
Test\SMULDualTests.c:50:test_SMUSD:PASS
Test\SMULDualTests.c:69:test_SMUSDX:PASS
Test\SMULDualTests.c:88:test_SMLAD:PASS
Test\SMULDualTests.c:107:test_SMLADX:PASS
Test\SMULDualTests.c:126:test_SMLSD:PASS
Test\SMULDualTests.c:145:test_SMLSDX:PASS
Test\SMULDualTests.c:164:test_SMLALD:PASS
Test\SMULDualTests.c:183:test_SMLALDX:PASS
Test\SMULDualTests.c:202:test_SMLSLD:PASS
Test\SMULDualTests.c:221:test_SMLSLDX:PASS

-----------------------
12 Tests 0 Failures 0 Ignored
OK

[stderr]
INFO:thumb2ISS:Loading elf SMULDualTests.Runner.out ...
Memory range : 0x0 - 0x4fff
Memory range : 0x20000000 - 0x2000152f
INFO:thumb2ISS:Simulation ended by end of execution (23138 steps simulated in 0.564 s)

```

**Debugger**
Add -d to command line, you will enter an interactive command line mode with disassembly and registers view
`> thumb2iss SMULDualTests.Runner.out -d`

```
00002dd8 :     #000048a8
00002ddc :     #000048b4
00002de0 :     #00004728
_lowstart:
00002de4 :   > ldr r0, [pc, #44]
00002de6 :     mov sp, r0
00002de8 :     ldr r1, [pc, #44]
00002dea :     ldr r2, [pc, #48]
00002dec :     subs r2, r2, r1
00002dee :     ble.n 2df8 <_lowstart+0x14>
00002df0 :     movs r0, #0
00002df2 :     str r0, [r1, r2]
00002df4 :     subs r2, #4

 --------------------------------------------------

R0 : 0x00000000    R1 : 0x00000000    R2 : 0x00000000    R3 : 0x00000000
R4 : 0x00000000    R5 : 0x00000000    R6 : 0x00000000    R7 : 0x00000000
R8 : 0x00000000    R9 : 0x00000000    R10: 0x00000000    R11: 0x00000000
R12: 0x00000000    SP : 0x20001530    LR : 0xffffffff    PC : 0x00002de4
N: 0 | Z: 0 | C: 0 | V: 0 | Q: 0 | GE: 0000

 __________________________________________________

. Next action: (siocurqbewmh) s
❯ Step over
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
                        mstdoutname

```

*Write Register* command allows to set a register as well as perform read-modify-write operations :
```
. Next action: Write register ...
|_ Register to write: r2|=0xF0F0
```
