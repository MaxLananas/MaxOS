[bits 16]

global _start

section .text
_start:
    jmp 0x0000:flush_cs
flush_cs:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00

    ; Charger le kernel à 0x1000
    mov ax, 0x1000
    mov es, ax
    xor bx, bx
    mov dh, 64      ; Nombre de secteurs à lire
    mov dl, [0x7DFE] ; Numéro du disque
    mov ah, 0x02    ; Fonction de lecture
    mov al, dh
    mov ch, 0x00    ; Cylindre 0
    mov cl, 0x02    ; Secteur 2
    mov dh, 0x00    ; Tête 0
    int 0x13

    ; Passer en mode 32 bits
    cli
    lgdt [gdtr]
    mov eax, cr0
    or eax, 0x1
    mov cr0, eax

    jmp 0x08:flush_gdt

[bits 32]
flush_gdt:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    jmp 0x10000

; GDT
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

gdtr:
    dw gdt_end - gdt_start - 1
    dd gdt_start