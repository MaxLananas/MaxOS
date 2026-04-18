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
    jc disk_error ; Jump if carry flag is set (error)

    ; Lire le kernel
    ; On suppose que le kernel fait 28 secteurs (14KB)
    ; On va lire 28 secteurs (0x1C) à partir du secteur 2 (0x02)
    ; vers l'adresse 0x0000:0x8000 (qui correspond à 0x8000 en mémoire linéaire)
    mov ah, 0x02          ; Service: Lire secteurs
    mov al, 28            ; Nombre de secteurs à lire
    mov ch, 0             ; Cylindre 0
    mov cl, 2             ; Secteur 2 (après le bootloader)
    mov dh, 0             ; Tête 0
    mov dl, [boot_drive]  ; Disque de boot
    xor bx, bx            ; Offset dans le buffer
    mov es, bx            ; Segment ES = 0x0000
    mov bx, 0x8000        ; Offset dans le buffer = 0x8000
    int 0x13
    jc disk_error ; Jump if carry flag is set (error)

    ; Vérifier la taille du kernel
    ; Le kernel est censé être à 0x8000.
    ; On va lire les 4 premiers octets pour obtenir la taille.
    ; On suppose que la taille est stockée en little-endian.
    mov esi, 0x8000       ; Adresse du début du kernel
    mov eax, [esi]        ; Lire les 4 premiers octets (taille du kernel)
    mov [kernel_size], eax

    ; Vérifier si la taille est raisonnable (par exemple, moins de 1MB)
    cmp eax, 1048576      ; 1MB
    ja kernel_too_large

    ; Mode protege
    cli
    lgdt [gdt_descriptor]
    mov eax, cr0
    or  eax, 1
    mov cr0, eax
    jmp CODE_SEG:start32

disk_error:
    ; Afficher un message d'erreur simple
    mov si, error_msg_disk
    call print_string
    cli
    hlt

kernel_too_large:
    ; Afficher un message d'erreur simple
    mov si, error_msg_kernel_size
    call print_string
    cli
    hlt

print_string:
    ; Affiche une chaîne de caractères terminée par 0
    ; SI pointe vers la chaîne
    mov ah, 0x0E ; Teletype output
.loop:
    lodsb
    or al, al
    jz .done
    int 0x10
    jmp .loop
.done:
    ret

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
    call 0x8000 ; Appel au kernel
    ; Ne jamais revenir ici
    cli
    hlt

[BITS 16]
boot_drive db 0
kernel_size dd 0

error_msg_disk db 'Erreur de lecture disque !', 0
error_msg_kernel_size db 'Taille du kernel trop grande !', 0

gdt_start:
dq 0
gdt_code:
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10011010b ; Present, Ring 0, Code, Executable, Read
    db 11001111b ; Granularity, 32-bit, Limit high
    db 0x00
gdt_data:
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10010010b ; Present, Ring 0, Data, ReadWrite
    db 11001111b ; Granularity, 32-bit, Limit high
    db 0x00
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1 ; Limit (size - 1)
    dd gdt_start              ; Base address

CODE_SEG equ gdt_code - gdt_start
DATA_SEG equ gdt_data - gdt_start

times 510-($-$$) db 0
dw 0xAA55
