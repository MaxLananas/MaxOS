[org 0x7C00]
[bits 16]

start:
    jmp 0x0000:flush_cs
flush_cs:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov si, msg
    call print_string

    mov ah, 0x02
    mov al, 1
    mov ch, 0
    mov dh, 0
    mov cl, 2
    mov bx, 0x1000
    int 0x13

    jmp 0x10000

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

msg db "Booting...", 0

times 510-($-$$) db 0
dw 0xAA55