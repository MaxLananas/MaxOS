[org 0x7C00]
[bits 16]

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov [BOOT_DRIVE], dl

    mov bx, MSG_REAL_MODE
    call print_string

    mov bx, 0x1000
    mov dh, 4
    mov dl, [BOOT_DRIVE]
    call disk_load

    jmp 0x10000

    jmp $

print_string:
    pusha
    mov ah, 0x0E
    .loop:
        mov al, [bx]
        cmp al, 0
        je .done
        int 0x10
        inc bx
        jmp .loop
    .done:
        popa
        ret

disk_load:
    pusha
    push dx

    mov ah, 0x02
    mov al, dh
    mov ch, 0x00
    mov dh, 0x00
    mov cl, 0x02

    int 0x13

    jc disk_error

    pop dx
    cmp al, dh
    jne disk_error
    popa
    ret

disk_error:
    mov bx, DISK_ERROR_MSG
    call print_string
    jmp $

BOOT_DRIVE: db 0
MSG_REAL_MODE: db "Booting from 16-bit Real Mode", 0
DISK_ERROR_MSG: db "Disk read error!", 0

times 510-($-$$) db 0
dw 0xAA55