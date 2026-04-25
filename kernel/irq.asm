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
    push eax
    mov eax, [esp + 12]
    push eax
    call irq_handler
    add esp, 4
    popa
    add esp, 8
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
    jmp irq_common_stub

irq15:
    push dword 0
    push dword 47
    jmp irq_common_stub