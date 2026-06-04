[org 0x7C00]
[bits 16]

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov [BOOT_DRIVE], dl

    mov si, msg_boot
    call print_string

    mov bx, 0x1000
    mov dh, 64
    mov dl, [BOOT_DRIVE]
    call disk_load

    jmp 0x1000:0x0000

    cli
    hlt

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

disk_load:
    push dx
    mov ah, 0x02
    mov al, dh
    mov ch, 0x00
    mov dh, 0x00
    mov cl, 0x02
    int 0x13
    jc disk_error
    pop dx
    cmp dh, al
    jne disk_error
    ret

disk_error:
    mov si, msg_disk_error
    call print_string
    jmp $

msg_boot db "Booting OS...", 0
msg_disk_error db "Disk read error!", 0

BOOT_DRIVE db 0

times 510 - ($ - $$) db 0
dw 0xAA55