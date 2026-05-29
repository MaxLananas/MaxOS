[bits 32]

global idt_load

extern idt_ptr

idt_load:
    mov eax, [esp + 4]
    lidt [eax]
    ret