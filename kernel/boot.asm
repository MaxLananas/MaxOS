BITS 32

section .boot
global _start

_start:
    jmp 0x10000

times 510-($-$$) db 0
dw 0xaa55