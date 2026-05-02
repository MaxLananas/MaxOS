BITS 32

global irq0
global irq1
global irq2
global irq3
global irq4
extern irq_handler

irq_common_stub:
    pusha
    push esp
    call irq_handler
    add esp, 8
    popa
    iret

irq0:
    push dword 0
    push dword 32
    jmp irq_common_stub

irq1:
    push dword 0
    push dword 33
    jmp irq_common_stub

irq2:
    push dword 0
    push dword 34
    jmp irq_common_stub

irq3:
    push dword 0
    push dword 35
    jmp irq_common_stub

irq4:
    push dword 0
    push dword 36
    jmp irq_common_stub

irq5:
    push dword 0
    push dword 37
    jmp irq_common_stub

irq6:
    push dword 0
    push dword 38
    jmp irq_common_stub

irq7:
    push dword 0
    push dword 39
    jmp irq_common_stub

irq8:
    push dword 0
    push dword 40
    jmp irq_common_stub

irq9:
    push dword 0
    push dword 41
    jmp irq_common_stub

irq10:
    push dword 0
    push dword 42
    jmp irq_common_stub

irq11:
    push dword 0
    push dword 43
    jmp irq_common_stub

irq12:
    push dword 0
    push dword 44
    jmp irq_common_stub

irq13:
    push dword 0
    push dword 45
    jmp irq_common_stub

irq14:
    push dword 0
    push dword 46
    jmp irq_common_st

irq15:
    push dword 0
    push dword 47
    jmp irq_common_stub