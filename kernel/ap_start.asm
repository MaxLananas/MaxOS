BITS 32

section .text
global ap_start

ap_start:
    mov eax, cr0
    and eax, 0x9FFFFFFF
    mov cr0, eax

    mov esp, [esi + 4]
    mov cr3, [esi + 16]

    mov eax, cr0
    or eax, 0x80000000
    mov cr0, eax

    jmp [esi]