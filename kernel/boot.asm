[org 0x7C00]
[bits 16]

start:
    mov ax, 0x07C0
    mov ds, ax
    mov ax, 0x8000
    mov ss, ax
    mov sp, 0xFFFF

    mov si, msg
    call print_string

    mov ah, 0x00
    mov al, 0x03
    int 0x10

    jmp 0x10000

msg db "Booting Bare Metal OS...", 0

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

times 510-($-$$) db 0
dw 0xAA55