bits 16

section .text
global _start

_start:
    mov ax, 0x07C0
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov sp, 0x7C00

    mov si, msg
    call print_string

    mov ah, 0x00
    int 0x16

    mov ax, 0x0003
    int 0x10

    mov eax, cr0
    or eax, 0x1
    mov cr0, eax

    jmp CODE_SEG:init_pm

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

bits 32
CODE_SEG equ 0x08

init_pm:
    mov ax, 0x10
    mov ds, ax
    mov ss, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ebp, 0x90000
    mov esp, ebp

    call kmain

    jmp $

msg db "Press any key to enter protected mode...", 0