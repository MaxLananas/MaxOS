[bits 32]
global irq0, irq1, irq2, irq3, irq4, irq5, irq6, irq7
global irq8, irq9, irq10, irq11, irq12, irq13, irq14, irq15

extern irq_handler

irq_common_stub:
    pusha
    push ds
    push es
    push fs
    push gs
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov eax, esp
    push eax
    mov eax, irq_handler
    call eax
    add esp, 4
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret

irq0:
    push 0
    push 32
    jmp irq_common_stub

irq1:
    push 0
    push 33
    jmp irq_common_stub

irq2:
    push 0
    push 34
    jmp irq_common_stub

irq3:
    push 0
    push 35
    jmp irq_common_stub

irq4:
    push 0
    push 36
    jmp irq_common_stub

irq5:
    push 0
    push 37
    jmp irq_common_stub

irq6:
    push 0
    push 38
    jmp irq_common_stub

irq7:
    push 0
    push 39
    jmp irq_common_stub

irq8:
    push 0
    push 40
    jmp irq_common_stub

irq9:
    push 0
    push 41
    jmp irq_common_stub

irq10:
    push 0
    push 42
    jmp irq_common_stub

irq11:
    push 0
    push 43
    jmp irq_common_stub

irq12:
    push 0
    push 44
    jmp irq_common_stub

irq13:
    push 0
    push 45
    jmp irq_common_stub

irq14:
    push 0
    push 46
    jmp irq_common_stub

irq15:
    push 0
    push 47
    jmp irq_common_stub