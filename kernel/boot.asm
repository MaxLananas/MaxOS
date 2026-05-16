BITS 16
org 0x7C00

start:
    jmp 0x0000:real_mode

real_mode:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    ; Save boot drive
    mov [boot_drive], dl

    ; Load kernel
    mov bx, 0x1000
    mov dh, 45
    mov dl, [boot_drive]
    call disk_load

    ; Switch to protected mode
    cli
    lgdt [gdt_descriptor]
    mov eax, cr0
    or eax, 0x1
    mov cr0, eax
    jmp CODE_SEG:init_pm

%include "gdt.asm"

disk_load:
    pusha
    mov di, 3
.read_sector:
    mov ah, 0x02
    mov al, 1
    mov ch, 0x00
    mov dh, 0x00
    mov cl, byte [sector]
    int 0x13
    jnc .next_sector
    dec di
    jnz .read_sector
    jmp disk_error
.next_sector:
    inc byte [sector]
    mov ax, es
    add ax, 0x20
    mov es, ax
    dec dh
    jnz .read_sector
    popa
    ret

disk_error:
    mov si, disk_error_msg
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

disk_error_msg db "Disk read error", 0
boot_drive db 0
sector db 2

times 510-($-$$) db 0
dw 0xAA55