BITS 32

global ap_start
extern kmain

section .text
ap_start:
    mov esp, _stack_top_ap
    call kmain
.hang:
    cli
    hlt
    jmp .hang

section .bss
    resb 16384
global _stack_top_ap
_stack_top_ap: