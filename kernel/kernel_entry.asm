global _start
extern _stack_top

section .text
_start:
    mov esp, _stack_top
    extern kernel_main
    call kernel_main
    jmp $