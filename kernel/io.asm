[bits 32]

global outb
global inb
global outw
global inw
global outl
global inl

outb:
    mov dx, [esp + 4]
    mov al, [esp + 8]
    out dx, al
    ret

inb:
    mov dx, [esp + 4]
    in al, dx
    ret

outw:
    mov dx, [esp + 4]
    mov ax, [esp + 8]
    out dx, ax
    ret

inw:
    mov dx, [esp + 4]
    in ax, dx
    ret

outl:
    mov dx, [esp + 4]
    mov eax, [esp + 8]
    out dx, eax
    ret

inl:
    mov dx, [esp + 4]
    in eax, dx
    ret