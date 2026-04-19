section .text
global irq0_handler

extern g_ticks
extern timer_irq_handler

irq0_handler:
    pushad
    call timer_irq_handler
    mov eax, [g_ticks]
    inc eax
    mov [g_ticks], eax
    popad
    iret