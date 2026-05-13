BITS 16

start:
    jmp 0x0000:after_bios

after_bios:
    mov ax, 0x0000
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    mov si, msg
    call print_string

    mov ah, 0x00
    mov al, 0x03
    int 0x10

    jmp 0x1000:0x0000

msg db "Booting...", 0

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