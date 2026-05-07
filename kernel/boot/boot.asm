BITS 16
ORG 0x7C00

start:
    jmp 0x0000:main

main:
    cli
    mov ax, 0
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    mov [drive], dl

    mov ah, 0x02
    mov al, 1
    mov ch, 0
    mov dh, 0
    mov cl, 2
    mov bx, 0x1000
    mov es, bx
    mov bx, 0
    int 0x13

    jmp 0x0000:0x1000

drive db 0

times 510-($-$$) db 0
dw 0xAA55