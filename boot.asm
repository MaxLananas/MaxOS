[bits 32]
[org 0x7C00]

start:
    mov ax, 0x07C0
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov sp, 0x7C00

    jmp 0x10000

times 510-($-$$) db 0
dw 0xAA55