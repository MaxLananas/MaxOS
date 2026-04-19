[bits 32]
[extern isr_handler]

global idt_load

section .text
idt_load:
    lidt [idtp]
    sti
    ret

section .data
idtp:
    dw 256*8-1
    dd 0