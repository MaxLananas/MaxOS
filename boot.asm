bits 16
org 0x7C00

start:
    jmp 0x0000:real_start
    times 3-($-$$) db 0

real_start:
    cli
    mov ax, 0
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    ; Load kernel
    mov ah, 0x02
    mov al, 64
    mov ch, 0
    mov dh, 0
    mov cl, 2
    mov bx, 0x1000
    mov es, bx
    mov bx, 0
    int 0x13

    jmp 0x1000:0x0000

times 510-($-$$) db 0
dw 0xAA55