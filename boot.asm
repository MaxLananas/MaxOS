[bits 16]
[org 0x7C00]

start:
    jmp 0x0000:flush_cs
    cli

flush_cs:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    mov [BOOT_DRIVE], dl

    mov ah, 0x02
    mov al, 1
    mov ch, 0
    mov dh, 0
    mov cl, 2
    mov dl, [BOOT_DRIVE]
    mov bx, 0x1000
    int 0x13

    jmp 0x1000

BOOT_DRIVE db 0

times 510-($-$$) db 0
dw 0xAA55