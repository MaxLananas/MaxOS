BITS 32

section .text
global _start

_start:
    jmp 0x10000
.hang:
    cli
    hlt
    jmp .hang