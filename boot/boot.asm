BITS 16

start:
    jmp 0x07C0:init

init:
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

    mov ah, 0x00
    mov al, 0x03
    int 0x10

    cli
    lgdt [gdt_descriptor]

    mov eax, cr0
    or eax, 0x1
    mov cr0, eax

    jmp CODE_SEG:init_pm

BITS 32
init_pm:
    mov ax, DATA_SEG
    mov ds, ax
    mov ss, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    mov ebp, 0x90000
    mov esp, ebp

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

msg db "Loading OS...", 0

gdt_start:
    gdt_null:
        dd 0x0
        dd 0x0
    gdt_code:
        dw 0xFFFF
        dw 0x0
        db 0x0
        db 0x9A
        db 0xCF
        db 0x0
    gdt_data:
        dw 0xFFFF
        dw 0x0
        db 0x0
        db 0x92
        db 0xCF
        db 0x0
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

CODE_SEG equ gdt_code - gdt_start
DATA_SEG equ gdt_data - gdt_start

times 510-($-$$) db 0
dw 0xAA55