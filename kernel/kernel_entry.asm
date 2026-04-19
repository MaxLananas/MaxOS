section .bss
    resb 16384
_stack_top:

section .text
    global _start
    extern kernel_main

_start:
    mov esp, _stack_top
    call kernel_main
    cli
.halt:
    hlt
    jmp .halt