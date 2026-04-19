[bits 16]

section .text
global _start

_start:
    jmp 0x0000:init_cs
init_cs:
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, _stack_top

    mov si, msg
    call print_string

    call check_a20
    jne a20_enabled

    call enable_a20
    call check_a20
    jne a20_enabled

    mov si, a20_fail
    call print_string
    jmp $

a20_enabled:
    cli

    lgdt [gdt_descriptor]

    mov eax, cr0
    or eax, 0x1
    mov cr0, eax

    jmp CODE_SEG:init_pm

[bits 32]
init_pm:
    mov ax, DATA_SEG
    mov ds, ax
    mov ss, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    mov ebp, _stack_top
    mov esp, ebp

    extern kmain
    call kmain

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

check_a20:
    pushf
    push ds
    push es
    push di
    push si

    xor ax, ax
    mov es, ax
    not ax
    mov ds, ax
    mov di, 0x0500
    mov si, 0x0510
    mov al, byte [es:di]
    push ax
    mov al, byte [ds:si]
    push ax
    mov byte [es:di], 0x00
    mov byte [ds:si], 0xFF
    cmp byte [es:di], 0xFF
    pop ax
    mov byte [ds:si], al
    pop ax
    mov byte [es:di], al

    mov ax, 0
    je check_a20_done
    mov ax, 1
check_a20_done:
    pop si
    pop di
    pop es
    pop ds
    popf
    ret

enable_a20:
    in al, 0x92
    or al, 2
    out 0x92, al
    ret

msg db "Booting...", 0
a20_fail db "A20 line not enabled", 0

gdt_start:
gdt_null:
    dq 0x0
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

_stack_top: