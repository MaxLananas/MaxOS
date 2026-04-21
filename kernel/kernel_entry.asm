global _start
extern kmain

section .text
_start:
    mov esp, _stack_top
    call kmain
    jmp $