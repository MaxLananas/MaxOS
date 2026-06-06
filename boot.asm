[bits 16]
org 0x7C00

start:
    jmp 0x0000:flush_cs
flush_cs:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov [drive_number], dl

    mov eax, 0x10000
    mov cr0, eax

    jmp 0x08:flush_cs32

[bits 32]
flush_cs32:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000

    jmp 0x10000

drive_number db 0

times 510-($-$$) db 0
dw 0xAA55