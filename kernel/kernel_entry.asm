global _stack_top
global _start

section .text
bits 32
_start:
    extern kmain
    call kmain
    cli
    hlt

section .bss
    resb 8192
_stack_top: