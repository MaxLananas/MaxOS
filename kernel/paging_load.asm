[bits 32]
global paging_load_directory

paging_load_directory:
    mov eax, [esp + 4]
    mov cr3, eax
    mov eax, cr0
    or eax, 0x80000000
    mov cr0, eax
    ret