[bits 32]

extern keyboard_handler
extern mouse_handler
extern timer_callback

keyboard_handler_wrapper:
    pusha
    call keyboard_handler
    popa
    iret

mouse_handler_wrapper:
    pusha
    call mouse_handler
    popa
    iret

timer_callback_wrapper:
    pusha
    call timer_callback
    popa
    iret