BITS 32

global irq0
global irq1
global irq2
global irq3
global irq4
global irq5
global irq6
global irq7
global irq8
global irq9
global irq10
global irq11
global irq12
global irq13
global irq14
global irq15

extern irq_handler

irq_common_stub:
    pusha
    push esp
    call irq_handler
    add esp, 4
    popa
    iret

irq0:
    push dword 0
    push dword 0
    jmp irq_common_stub

irq1:
    push dword 0
    push dword 1
    jmp irq_common_stub

irq2:
    push dword 0
    push dword 2
    jmp irq_common_stub

irq3:
    push dword 0
    push dword 3
    jmp irq_common_stub

irq4:
    push dword 0
    push dword 4
    jmp irq_common_stub

irq5:
    push dword 0
    push dword 5
    jmp irq_common_stub

irq6:
    push dword 0
    push dword 6
    jmp irq_common_stub

irq7:
    push dword 0
    push dword 7
    jmp irq_common_stub

irq8:
    push dword 0
    push dword 8
    jmp irq_common_stub

irq9:
    push dword 0
    push dword 9
    jmp irq_common_stub

irq10:
    push dword 0
    push dword 10
    jmp irq_common_stub

irq11:
    push dword 0
    push dword 11
    jmp irq_common_stub

irq12:
    push dword 0
    push dword 12
    jmp irq_common_stub

irq13:
    push dword 0
    push dword 13
    jmp irq_common_stub

irq14:
    push dword 0
    push dword 14
    jmp irq_common_stub

irq15:
    push dword 0
    push dword 15
    jmp irq_common_stub