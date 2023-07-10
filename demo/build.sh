#!/bin/sh

arm-none-eabi-gcc -O2 --specs=rdimon.specs -mthumb -g -nostartfiles -T gcc_arm.ld -mcpu=cortex-m4 -lc -lrdimon main.c startup_ARMCM4.S -o hello_world-cm4.out
