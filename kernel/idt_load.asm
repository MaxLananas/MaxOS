[bits 32]
extern idt_ptr

global idt_load
idt_load:
    lidt [idt_ptr]
    ret