[bits 32]

; ISRs 0-31 (CPU exceptions)
global isr0
global isr1
global isr2
global isr3
global isr4
global isr5
global isr6
global isr7
global isr8
global isr9
global isr10
global isr11
global isr12
global isr13
global isr14
global isr15
global isr16
global isr17
global isr18
global isr19
global isr20
global isr21
global isr22
global isr23
global isr24
global isr25
global isr26
global isr27
global isr28
global isr29
global isr30
global isr31

; ISRs 32-47 (IRQs)
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
global irq16
global irq17
global irq18
global irq19
global irq20
global irq21
global irq22
global irq23
global irq24
global irq25
global irq26
global irq27
global irq28
global irq29
global irq30
global irq31
global irq32
global irq33
global irq34
global irq35
global irq36
global irq37
global irq38
global irq39
global irq40
global irq41
global irq42
global irq43
global irq44
global irq45
global irq46
global irq47

extern isr_handler
extern irq_handler

; Common ISR stub
isr_common_stub:
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
    push esp
    call isr_handler
    add esp, 4
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret

; Common IRQ stub
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
    push esp
    call irq_handler
    add esp, 4
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret

; ISRs 0-31
isr0:
    push dword 0
    push dword 0
    jmp isr_common_stub

isr1:
    push dword 0
    push dword 1
    jmp isr_common_stub

isr2:
    push dword 0
    push dword 2
    jmp isr_common_stub

isr3:
    push dword 0
    push dword 3
    jmp isr_common_stub

isr4:
    push dword 0
    push dword 4
    jmp isr_common_stub

isr5:
    push dword 0
    push dword 5
    jmp isr_common_stub

isr6:
    push dword 0
    push dword 6
    jmp isr_common_stub

isr7:
    push dword 0
    push dword 7
    jmp isr_common_stub

isr8:
    push dword 8
    jmp isr_common_stub

isr9:
    push dword 0
    push dword 9
    jmp isr_common_stub

isr10:
    push dword 10
    jmp isr_common_stub

isr11:
    push dword 11
    jmp isr_common_stub

isr12:
    push dword 12
    jmp isr_common_stub

isr13:
    push dword 13
    jmp isr_common_stub

isr14:
    push dword 14
    jmp isr_common_stub

isr15:
    push dword 0
    push dword 15
    jmp isr_common_stub

isr16:
    push dword 0
    push dword 16
    jmp isr_common_stub

isr17:
    push dword 17
    jmp isr_common_stub

isr18:
    push dword 0
    push dword 18
    jmp isr_common_stub

isr19:
    push dword 0
    push dword 19
    jmp isr_common_stub

isr20:
    push dword 0
    push dword 20
    jmp isr_common_stub

isr21:
    push dword 0
    push dword 21
    jmp isr_common_stub

isr22:
    push dword 0
    push dword 22
    jmp isr_common_stub

isr23:
    push dword 0
    push dword 23
    jmp isr_common_stub

isr24:
    push dword 0
    push dword 24
    jmp isr_common_stub

isr25:
    push dword 0
    push dword 25
    jmp isr_common_stub

isr26:
    push dword 0
    push dword 26
    jmp isr_common_stub

isr27:
    push dword 0
    push dword 27
    jmp isr_common_stub

isr28:
    push dword 0
    push dword 28
    jmp isr_common_stub

isr29:
    push dword 0
    push dword 29
    jmp isr_common_stub

isr30:
    push dword 0
    push dword 30
    jmp isr_common_stub

isr31:
    push dword 0
    push dword 31
    jmp isr_common_stub

; IRQs 0-15
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

irq16:
    push dword 0
    push dword 48
    jmp irq_common_stub

irq17:
    push dword 0
    push dword 49
    jmp irq_common_stub

irq18:
    push dword 0
    push dword 50
    jmp irq_common_stub

irq19:
    push dword 0
    push dword 51
    jmp irq_common_stub

irq20:
    push dword 0
    push dword 52
    jmp irq_common_stub

irq21:
    push dword 0
    push dword 53
    jmp irq_common_stub

irq22:
    push dword 0
    push dword 54
    jmp irq_common_stub

irq23:
    push dword 0
    push dword 55
    jmp irq_common_stub

irq24:
    push dword 0
    push dword 56
    jmp irq_common_stub

irq25:
    push dword 0
    push dword 57
    jmp irq_common_stub

irq26:
    push dword 0
    push dword 58
    jmp irq_common_stub

irq27:
    push dword 0
    push dword 59
    jmp irq_common_stub

irq28:
    push dword 0
    push dword 60
    jmp irq_common_stub

irq29:
    push dword 0
    push dword 61
    jmp irq_common_stub

irq30:
    push dword 0
    push dword 62
    jmp irq_common_stub

irq31:
    push dword 0
    push dword 63
    jmp irq_common_stub

irq32:
    push dword 0
    push dword 64
    jmp irq_common_stub

irq33:
    push dword 0
    push dword 65
    jmp irq_common_stub

irq34:
    push dword 0
    push dword 66
    jmp irq_common_stub

irq35:
    push dword 0
    push dword 67
    jmp irq_common_stub

irq36:
    push dword 0
    push dword 68
    jmp irq_common_stub

irq37:
    push dword 0
    push dword 69
    jmp irq_common_stub

irq38:
    push dword 0
    push dword 70
    jmp irq_common_stub

irq39:
    push dword 0
    push dword 71
    jmp irq_common_stub

irq40:
    push dword 0
    push dword 72
    jmp irq_common_stub

irq41:
    push dword 0
    push dword 73
    jmp irq_common_stub

irq42:
    push dword 0
    push dword 74
    jmp irq_common_stub

irq43:
    push dword 0
    push dword 75
    jmp irq_common_stub

irq44:
    push dword 0
    push dword 76
    jmp irq_common_stub

irq45:
    push dword 0
    push dword 77
    jmp irq_common_stub

irq46:
    push dword 0
    push dword 78
    jmp irq_common_stub

irq47:
    push dword 0
    push dword 79
    jmp irq_common_stub