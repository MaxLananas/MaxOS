[bits 32]

extern timer_handler

timer_handler_asm:
    pushad
    call timer_handler
    popad
    iret