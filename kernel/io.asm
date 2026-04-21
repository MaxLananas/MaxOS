bits 32

section .text

global inb
global outb

inb:
    mov dx, [esp + 4]
    in al, dx
    ret

outb:
    mov dx, [esp + 4]
    mov al, [esp + 8]
    out dx, al
    ret