ORG 0x7C00
BITS 16

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov [BOOT_DRIVE], dl

    mov bx, 0x1000
    mov es, bx
    mov bx, 0x0

    mov dh, 64
    mov dl, [BOOT_DRIVE]
    mov cx, 0x0002
    call disk_load

    jmp 0x1000:0x0000

    jmp $

disk_load:
    pusha
    mov di, 3
.read_sector:
    mov ah, 0x02
    mov al, 0x01
    mov ch, 0x00
    mov cl, byte [bp + 6]
    mov dh, 0x00
    int 0x13
    jnc .next_sector
    dec di
    jnz .read_sector
    jmp disk_error
.next_sector:
    mov si, [bp + 6]
    inc si
    mov [bp + 6], si
    mov ax, [bp + 2]
    add ax, 0x200
    mov [bp + 2], ax
    cmp si, dh
    jl .read_sector
    popa
    ret

disk_error:
    mov si, DISK_ERROR_MSG
    call print_string
    jmp $

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

BOOT_DRIVE: db 0
DISK_ERROR_MSG: db "Disk read error", 0

times 510-($-$$) db 0
dw 0xAA55