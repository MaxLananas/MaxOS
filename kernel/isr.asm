BITS 32

section .text

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
global isr32
global isr33
global isr34
global isr35
global isr36
global isr37
global isr38
global isr39
global isr40
global isr41
global isr42
global isr43
global isr44
global isr45
global is46
global isr47

extern isr_handler

isr0:
    push byte 0
    push byte 0
    jmp isr_common_stub

isr1:
    push byte 0
    push byte 1
    jmp isr_common_stub

isr2:
    push byte 0
    push byte 2
    jmp isr_common_stub

isr3:
    push byte 0
    push byte 3
    jmp isr_common_stub

isr4:
    push byte 0
    push byte 4
    jmp isr_common_stub

isr5:
    push byte 0
    push byte 5
    jmp isr_common_stub

isr6:
    push byte 0
    push byte 6
    jmp isr_common_stub

isr7:
    push byte 0
    push byte 7
    jmp isr_common_stub

isr8:
    push byte 8
    jmp isr_common_stub

isr9:
    push byte 0
    push byte 9
    jmp isr_common_stub

isr10:
    push byte 10
    jmp isr_common_stub

isr11:
    push byte 11
    jmp isr_common_stub

isr12:
    push byte 12
    jmp isr_common_stub

isr13:
    push byte 13
    jmp isr_common_stub

isr14:
    push byte 14
    jmp isr_common_stub

isr15:
    push byte 0
    push byte 15
    jmp isr_common_stub

isr16:
    push byte 0
    push byte 16
    jmp isr_common_stub

isr17:
    push byte 17
    jmp isr_common_stub

isr18:
    push byte 0
    push byte 18
    jmp isr_common_stub

isr19:
    push byte 0
    push byte 19
    jmp isr_common_stub

isr20:
    push byte 0
    push byte 20
    jmp isr_common_stub

isr21:
    push byte 0
    push byte 21
    jmp isr_common_stub

isr22:
    push byte 0
    push byte 22
    jmp isr_common_stub

isr23:
    push byte 0
    push byte 23
    jmp isr_common_stub

isr24:
    push byte 0
    push byte 24
    jmp isr_common_stub

isr25:
    push byte 0
    push byte 25
    jmp isr_common_stub

isr26:
    push byte 0
    push byte 26
    jmp isr_common_stub

isr27:
    push byte 0
    push byte 27
    jmp isr_common_stub

isr28:
    push byte 0
    push byte 28
    jmp isr_common_stub

isr29:
    push byte 0
    push byte 29
    jmp isr_common_stub

isr30:
    push byte 0
    push byte 30
    jmp isr_common_stub

isr31:
    push byte 0
    push byte 31
    jmp isr_common_stub

isr32:
    push byte 0
    push byte 32
    jmp isr_common_stub

isr33:
    push byte 0
    push byte 33
    jmp isr_common_stub

isr34:
    push byte 0
    push byte 34
    jmp isr_common_stub

isr35:
    push byte 0
    push byte 35
    jmp isr_common_stub

isr36:
    push byte 0
    push byte 36
    jmp isr_common_stub

isr37:
    push byte 0
    push byte 37
    jmp isr_common_stub

isr38:
    push byte 0
    push byte 38
    jmp isr_common_stub

isr39:
    push byte 0
    push byte 39
    jmp isr_common_stub

isr40:
    push byte 0
    push byte 40
    jmp isr_common_stub

isr41:
    push byte 0
    push byte 41
    jmp isr_common_stub

isr42:
    push byte 0
    push byte 42
    jmp isr_common_stub

isr43:
    push byte 0
    push byte 43
    jmp isr_common_stub

isr44:
    push byte 0
    push byte 44
    jmp isr_common_stub

isr45:
    push byte 0
    push byte 45
    jmp isr_common_stub

isr46:
    push byte 0
    push byte 46
    jmp isr_common_stub

isr47:
    push byte 0
    push byte 47
    jmp isr_common_stub

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