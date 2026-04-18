[BITS 16]
[ORG 0x7C00]

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    mov [boot_drive], dl
    sti

    ; Reset disque
    xor ah, ah
    mov dl, [boot_drive]
    int 0x13

    ; Lire 28 secteurs vers 0x0000:0x8000
    mov ah, 0x02
    mov al, 28
    mov ch, 0
    mov cl, 2
    mov dh, 0
    mov dl, [boot_drive]
    xor bx, bx
    mov es, bx
    mov bx, 0x8000
    int 0x13

    ; Mode protege
    cli
    lgdt [gdt_descriptor]
    mov eax, cr0
    or  eax, 1
    mov cr0, eax
    jmp CODE_SEG:start32

[BITS 32]
start32:
    mov ax, DATA_SEG
    mov ds, ax
    mov ss, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ebp, 0x90000
    mov esp, ebp
    call 0x8000
    ; Ne jamais revenir ici
    cli
    hlt

[BITS 16]
boot_drive db 0

gdt_start:
    dq 0
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

CODE_SEG equ gdt_code - gdt_start
DATA_SEG equ gdt_data - gdt_start

times 510-($-$$) db 0
dw 0xAA55