section .text
global irq_handler
global keyboard_handler
global timer_handler

extern g_ticks
extern keyboard_irq_handler

irq_handler:
    pusha
    mov eax, [esp+32]
    cmp eax, 32
    je timer_irq
    cmp eax, 33
    je keyboard_irq
    jmp irq_end

timer_irq:
    call timer_handler
    jmp irq_end

keyboard_irq:
    call keyboard_handler
    jmp irq_end

irq_end:
    mov al, 0x20
    out 0x20, al
    cmp byte [esp+32], 39
    jb .skip_slave
    out 0xA0, al
.skip_slave:
    popa
    ret

timer_handler:
    push eax
    mov eax, [g_ticks]
    inc eax
    mov [g_ticks], eax
    pop eax
    ret

keyboard_handler:
    pusha
    call keyboard_irq_handler
    popa
    ret