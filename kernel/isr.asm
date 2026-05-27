[bits 32]

; Déclarations globales pour toutes les ISR
global isr0, isr1, isr2, isr3, isr4, isr5, isr6, isr7, isr8, isr9
global isr10, isr11, isr12, isr13, isr14, isr15, isr16, isr17, isr18, isr19
global isr20, isr21, isr22, isr23, isr24, isr25, isr26, isr27, isr28, isr29
global isr30, isr31, isr32, isr33, isr34, isr35, isr36, isr37, isr38, isr39
global isr40, isr41, isr42, isr43, isr44, isr45, isr46, isr47

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
    mov eax, esp
    push eax
    mov eax, isr_handler
    call eax
    add esp, 4
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret

; ISR sans code d'erreur
isr0:
    push 0
    push 0
    jmp isr_common_stub

isr1:
    push 0
    push 1
    jmp isr_common_stub

isr2:
    push 0
    push 2
    jmp isr_common_stub

isr3:
    push 0
    push 3
    jmp isr_common_stub

isr4:
    push 0
    push 4
    jmp isr_common_stub

isr5:
    push 0
    push 5
    jmp isr_common_stub

isr6:
    push 0
    push 6
    jmp isr_common_stub

isr7:
    push 0
    push 7
    jmp isr_common_stub

isr8:
    push 8
    jmp isr_common_stub

isr9:
    push 0
    push 9
    jmp isr_common_stub

isr10:
    push 10
    jmp isr_common_stub

isr11:
    push 11
    jmp isr_common_stub

isr12:
    push 12
    jmp isr_common_stub

isr13:
    push 13
    jmp isr_common_stub

isr14:
    push 14
    jmp isr_common_stub

isr15:
    push 0
    push 15
    jmp isr_common_stub

isr16:
    push 0
    push 16
    jmp isr_common_stub

isr17:
    push 17
    jmp isr_common_stub

isr18:
    push 0
    push 18
    jmp isr_common_stub

isr19:
    push 0
    push 19
    jmp isr_common_stub

isr20:
    push 0
    push 20
    jmp isr_common_stub

isr21:
    push 0
    push 21
    jmp isr_common_stub

isr22:
    push 0
    push 22
    jmp isr_common_stub

isr23:
    push 0
    push 23
    jmp isr_common_stub

isr24:
    push 0
    push 24
    jmp isr_common_stub

isr25:
    push 0
    push 25
    jmp isr_common_stub

isr26:
    push 0
    push 26
    jmp isr_common_stub

isr27:
    push 0
    push 27
    jmp isr_common_stub

isr28:
    push 0
    push 28
    jmp isr_common_stub

isr29:
    push 0
    push 29
    jmp isr_common_stub

isr30:
    push 0
    push 30
    jmp isr_common_stub

isr31:
    push 0
    push 31
    jmp isr_common_stub

; IRQ 0-15
isr32:
    push 0
    push 32
    jmp isr_common_stub

isr33:
    push 0
    push 33
    jmp isr_common_stub

isr34:
    push 0
    push 34
    jmp isr_common_stub

isr35:
    push 0
    push 35
    jmp isr_common_stub

isr36:
    push 0
    push 36
    jmp isr_common_stub

isr37:
    push 0
    push 37
    jmp isr_common_stub

isr38:
    push 0
    push 38
    jmp isr_common_stub

isr39:
    push 0
    push 39
    jmp isr_common_stub

isr40:
    push 0
    push 40
    jmp isr_common_stub

isr41:
    push 0
    push 41
    jmp isr_common_stub

isr42:
    push 0
    push 42
    jmp isr_common_stub

isr43:
    push 0
    push 43
    jmp isr_common_stub

isr44:
    push 0
    push 44
    jmp isr_common_stub

isr45:
    push 0
    push 45
    jmp isr_common_stub

isr46:
    push 0
    push 46
    jmp isr_common_stub

isr47:
    push 0
    push 47
    jmp isr_common_stub