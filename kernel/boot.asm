[bits 16]
org 0x7c00

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    mov [boot_drive], dl

    ; Load kernel from disk
    mov bx, 0x1000
    mov dh, 64
    mov dl, [boot_drive]
    call disk_load

    jmp 0x1000

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
    mov si, disk_error_msg
    call print_string
    jmp $

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0e
    int 0x10
    jmp print_string
.done:
    ret

disk_error_msg db "Disk read error", 0

boot_drive db 0

times 510 - ($ - $$) db 0
dw 0xaa55