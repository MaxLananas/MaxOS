[bits 16]
[org 0x7C00]

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov si, msg_boot
    call print_string

    mov ah, 0x02
    mov al, 0x04
    mov ch, 0x00
    mov dh, 0x00
    mov cl, 0x02
    mov bx, 0x1000
    int 0x13

    jmp 0x1000:0x0000

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

msg_boot db "Booting...", 0