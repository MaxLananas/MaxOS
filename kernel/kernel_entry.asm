global _stack_top
global _start

section .bss
    resb 16384
_stack_top:

section .text
bits 32
_start:
    extern kernel_main
    mov esp, _stack_top
    call kernel_main
    cli
    hlt