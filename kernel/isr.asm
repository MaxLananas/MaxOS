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
extern irq_handler

isr0:  push 0  \n  push 0  \n  jmp isr_common_stub
isr1:  push 0  \n  push 1  \n  jmp isr_common_stub
isr2:  push 0  \n  push 2  \n  jmp isr_common_stub
isr3:  push 0  \n  push 3  \n  jmp isr_common_stub
isr4:  push 0  \n  push 4  \n  jmp isr_common_stub
isr5:  push 0  \n  push 5  \n  jmp isr_common_stub
isr6:  push 0  \n  push 6  \n  jmp isr_common_stub
isr7:  push 0  \n  push 7  \n  jmp isr_common_stub
isr8:  push 8  \n  jmp isr_common_stub
isr9:  push 0  \n  push 9  \n  jmp isr_common_stub
isr10: push 10 \n  jmp isr_common_stub
isr11: push 11 \n  jmp isr_common_stub
isr12: push 12 \n  jmp isr_common_stub
isr13: push 13 \n  jmp isr_common_stub
isr14: push 14 \n  jmp isr_common_stub
isr15: push 0  \n  push 15 \n  jmp isr_common_stub
isr16: push 0  \n  push 16 \n  jmp isr_common_stub
isr17: push 17 \n  jmp isr_common_stub
isr18: push 0  \n  push 18 \n  jmp isr_common_stub
isr19: push 0  \n  push 19 \n  jmp isr_common_stub
isr20: push 0  \n  push 20 \n  jmp isr_common_stub
isr21: push 0  \n  push 21 \n  jmp isr_common_stub
isr22: push 0  \n  push 22 \n  jmp isr_common_stub
isr23: push 0  \n  push 23 \n  jmp isr_common_stub
isr24: push 0  \n  push 24 \n  jmp isr_common_stub
isr25: push 0  \n  push 25 \n  jmp isr_common_stub
isr26: push 0  \n  push 26 \n  jmp isr_common_stub
isr27: push 0  \n  push 27 \n  jmp isr_common_stub
isr28: push 0  \n  push 28 \n  jmp isr_common_stub
isr29: push 0  \n  push 29 \n  jmp isr_common_stub
isr30: push 0  \n  push 30 \n  jmp isr_common_stub
isr31: push 0  \n  push 31 \n  jmp isr_common_stub

isr32: push 0  \n  push 32 \n  jmp irq_common_stub
isr33: push 0  \n  push 33 \n  jmp irq_common_stub
isr34: push 0  \n  push 34 \n  jmp irq_common_stub
isr35: push 0  \n  push 35 \n  jmp irq_common_stub
isr36: push 0  \n  push 36 \n  jmp irq_common_stub
isr37: push 0  \n  push 37 \n  jmp irq_common_stub
isr38: push 0  \n  push 38 \n  jmp irq_common_stub
isr39: push 0  \n  push 39 \n  jmp irq_common_stub
isr40: push 0  \n  push 40 \n  jmp irq_common_stub
isr41: push 0  \n  push 41 \n  jmp irq_common_stub
isr42: push 0  \n  push 42 \n  jmp irq_common_stub
isr43: push 0  \n  push 43 \n  jmp irq_common_stub
isr44: push 0  \n  push 44 \n  jmp irq_common_stub
isr45: push 0  \n  push 45 \n  jmp irq_common_stub
isr46: push 0  \n  push 46 \n  jmp irq_common_stub
isr47: push 0  \n  push 47 \n  jmp irq_common_stub

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
    pop eax
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret

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
    pop eax
    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret
