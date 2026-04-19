BITS 32

section .text
global _stack_top
global _start

_start:
    mov esp, _stack_top
    extern kmain
    call kmain
    cli
    hlt

section .bss
resb 8192
_stack_top: