BITS 16

global _start

_start:
    mov ax, 0x07C0
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    mov ax, 0x0000
    mov ss, ax
    mov sp, 0x7C00

    mov si, msg
    call print_string

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