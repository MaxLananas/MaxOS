[bits 32]
[extern _stack_top]
[extern kmain]

global _start
_start:
    mov esp, _stack_top
    call kmain
    cli
.hang:
    hlt
    jmp .hang