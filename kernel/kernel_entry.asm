BITS 32
global _start
extern kmain

section .bss
    resb 16384
global _stack_top
_stack_top:

section .text
_start:
    mov esp, _stack_top
    call kmain
.hang:
    cli
    hlt
    jmp .hang