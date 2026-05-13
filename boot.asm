BITS 32
section .multiboot
align 4
    dd 0x1BADB002
    dd 0x00000003
    dd -(0x1BADB002 + 0x00000003)

section .text
global _start
extern _stack_top

_start:
    mov esp, _stack_top
    jmp 0x10000