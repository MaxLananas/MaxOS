BITS 32

section .text

global isr0
isr0:
    push byte 0
    push byte 0
    jmp isr_common_stub

global isr1
isr1:
    push byte 0
    push byte 1
    jmp isr_common_stub

global isr2
isr2:
    push byte 0
    push byte 2
    jmp isr_common_stub

global isr3
isr3:
    push byte 0
    push byte 3
    jmp isr_common_stub

global isr4
isr4:
    push byte 0
    push byte 4
    jmp isr_common_stub

global isr5
isr5:
    push byte 0
    push byte 5
    jmp isr_common_stub

global isr6
isr6:
    push byte 0
    push byte 6
    jmp isr_common_stub

global isr7
isr7:
    push byte 0
    push byte 7
    jmp isr_common_stub

global isr8
isr8:
    push byte 8
    jmp isr_common_stub

global isr9
isr9:
    push byte 0
    push byte 9
    jmp isr_common_stub

global isr10
isr10:
    push byte 10
    jmp isr_common_stub

global isr11
isr11:
    push byte 11
    jmp isr_common_stub

global isr12
isr12:
    push byte 12
    jmp isr_common_stub

global isr13
isr13:
    push byte 13
    jmp isr_common_stub

global isr14
isr14:
    push byte 14
    jmp isr_common_stub

global isr15
isr15:
    push byte 0
    push byte 15
    jmp isr_common_stub

global isr16
isr16:
    push byte 0
    push byte 16
    jmp isr_common_stub

global isr17
isr17:
    push byte 0
    push byte 17
    jmp isr_common_stub

global isr18
isr18:
    push byte 0
    push byte 18
    jmp isr_common_stub

global isr19
isr19:
    push byte 0
    push byte 19
    jmp isr_common_stub

global isr20
isr20:
    push byte 0
    push byte 20
    jmp isr_common_stub

global isr21
isr21:
    push byte 0
    push byte 21
    jmp isr_common_stub

global isr22
isr22:
    push byte 0
    push byte 22
    jmp isr_common_stub

global isr23
isr23:
    push byte 0
    push byte 23
    jmp isr_common_stub

global isr24
isr24:
    push byte 0
    push byte 24
    jmp isr_common_stub

global isr25
isr25:
    push byte 0
    push byte 25
    jmp isr_common_stub

global isr26
isr26:
    push byte 0
    push byte 26
    jmp isr_common_stub

global isr27
isr27:
    push byte 0
    push byte 27
    jmp isr_common_stub

global isr28
isr28:
    push byte 0
    push byte 28
    jmp isr_common_stub

global isr29
isr29:
    push byte 0
    push byte 29
    jmp isr_common_stub

global isr30
isr30:
    push byte 0
    push byte 30
    jmp isr_common_stub

global isr31
isr31:
    push byte 0
    push byte 31
    jmp isr_common_stub

global isr32
isr32:
    push byte 0
    push byte 32
    jmp isr_common_stub

global isr33
isr33:
    push byte 0
    push byte 33
    jmp isr_common_stub

global isr34
isr34:
    push byte 0
    push byte 34
    jmp isr_common_stub

global isr35
isr35:
    push byte 0
    push byte 35
    jmp isr_common_stub

global isr36
isr36:
    push byte 0
    push byte 36
    jmp isr_common_stub

global isr37
isr37:
    push byte 0
    push byte 37
    jmp isr_common_stub

global isr38
isr38:
    push byte 0
    push byte 38
    jmp isr_common_stub

global isr39
isr39:
    push byte 0
    push byte 39
    jmp isr_common_stub

global isr40
isr40:
    push byte 0
    push byte 40
    jmp isr_common_stub

global isr41
isr41:
    push byte 0
    push byte 41
    jmp isr_common_stub

global isr42
isr42:
    push byte 0
    push byte 42
    jmp isr_common_stub

global isr43
isr43:
    push byte 0
    push byte 43
    jmp isr_common_stub

global isr44
isr44:
    push byte 0
    push byte 44
    jmp isr_common_stub

global isr45
isr45:
    push byte 0
    push byte 45
    jmp isr_common_stub

global isr46
isr46:
    push byte 0
    push byte 46
    jmp isr_common_stub

global isr47
isr47:
    push byte 0
    push byte 47
    jmp isr_common_stub

extern isr_handler

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