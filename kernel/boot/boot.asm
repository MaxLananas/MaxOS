BITS 16
ORG 0x7C00

start:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    ; Activer A20
    in al, 0x92
    or al, 2
    out 0x92, al

    ; Charger GDT
    lgdt [gdt_descriptor]

    ; Passer en mode protégé
    mov eax, cr0
    or eax, 1
    mov cr0, eax

    jmp 0x08:init_pm

BITS 32
init_pm:
    mov ax, 0x10
    mov ds, ax
    mov ss, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    ; Sauter à 0x10000 (1MB)
    jmp 0x08:0x10000

gdt_start:
    dq 0x0
gdt_code:
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10011010b
    db 11001111b
    db 0x00
gdt_data:
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10010010b
    db 11001111b
    db 0x00
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

times 510-($-$$) db 0
dw 0xAA55