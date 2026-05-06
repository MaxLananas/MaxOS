BITS 32

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
global isr46
global isr47

extern isr_handler

isr_common_stub:
    pusha
    mov ax, ds
    push eax
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    push esp
    call isr_handler
    add esp, 4
    pop eax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    popa
    add esp, 8
    iret

isr0:
    cli
    push dword 0
    push dword 0
    jmp isr_common_stub

isr1:
    cli
    push dword 0
    push dword 1
    jmp isr_common_stub

isr2:
    cli
    push dword 0
    push dword 2
    jmp isr_common_stub

isr3:
    cli
    push dword 0
    push dword 3
    jmp isr_common_stub

isr4:
    cli
    push dword 0
    push dword 4
    jmp isr_common_stub

isr5:
    cli
    push dword 0
    push dword 5
    jmp isr_common_stub

isr6:
    cli
    push dword 0
    push dword 6
    jmp isr_common_stub

isr7:
    cli
    push dword 0
    push dword 7
    jmp isr_common_stub

isr8:
    cli
    push dword 8
    jmp isr_common_stub

isr9:
    cli
    push dword 0
    push dword 9
    jmp isr_common_stub

isr10:
    cli
    push dword 10
    jmp isr_common_stub

isr11:
    cli
    push dword 11
    jmp isr_common_stub

isr12:
    cli
    push dword 12
    jmp isr_common_stub

isr13:
    cli
    push dword 13
    jmp isr_common_stub

isr14:
    cli
    push dword 14
    jmp isr_common_stub

isr15:
    cli
    push dword 0
    push dword 15
    jmp isr_common_stub

isr16:
    cli
    push dword 0
    push dword 16
    jmp isr_common_stub

isr17:
    cli
    push dword 0
    push dword 17
    jmp isr_common_stub

isr18:
    cli
    push dword 0
    push dword 18
    jmp isr_common_stub

isr19:
    cli
    push dword 0
    push dword 19
    jmp isr_common_stub

isr20:
    cli
    push dword 0
    push dword 20
    jmp isr_common_stub

isr21:
    cli
    push dword 0
    push dword 21
    jmp isr_common_stub

isr22:
    cli
    push dword 0
    push dword 22
    jmp isr_common_stub

isr23:
    cli
    push dword 0
    push dword 23
    jmp isr_common_stub

isr24:
    cli
    push dword 0
    push dword 24
    jmp isr_common_stub

isr25:
    cli
    push dword 0
    push dword 25
    jmp isr_common_stub

isr26:
    cli
    push dword 0
    push dword 26
    jmp isr_common_stub

isr27:
    cli
    push dword 0
    push dword 27
    jmp isr_common_stub

isr28:
    cli
    push dword 0
    push dword 28
    jmp isr_common_stub

isr29:
    cli
    push dword 0
    push dword 29
    jmp isr_common_stub

isr30:
    cli
    push dword 0
    push dword 30
    jmp isr_common_stub

isr31:
    cli
    push dword 0
    push dword 31
    jmp isr_common_stub

isr32:
    cli
    push dword 0
    push dword 32
    jmp isr_common_stub

isr33:
    cli
    push dword 0
    push dword 33
    jmp isr_common_stub

isr34:
    cli
    push dword 0
    push dword 34
    jmp isr_common_stub

isr35:
    cli
    push dword 0
    push dword 35
    jmp isr_common_stub

isr36:
    cli
    push dword 0
    push dword 36
    jmp isr_common_stub

isr37:
    cli
    push dword 0
    push dword 37
    jmp isr_common_stub

isr38:
    cli
    push dword 0
    push dword 38
    jmp isr_common_stub

isr39:
    cli
    push dword 0
    push dword 39
    jmp isr_common_stub

isr40:
    cli
    push dword 0
    push dword 40
    jmp isr_common_stub

isr41:
    cli
    push dword 0
    push dword 41
    jmp isr_common_stub

isr42:
    cli
    push dword 0
    push dword 42
    jmp isr_common_stub

isr43:
    cli
    push dword 0
    push dword 43
    jmp isr_common_stub

isr44:
    cli
    push dword 0
    push dword 44
    jmp isr_common_stub

isr45:
    cli
    push dword 0
    push dword 45
    jmp isr_common_stub

isr46:
    cli
    push dword 0
    push dword 46
    jmp isr_common_stub

isr47:
    cli
    push dword 0
    push dword 47
    jmp isr_common_stub