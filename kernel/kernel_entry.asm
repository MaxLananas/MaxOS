BITS 32
global _start
global _stack_top
extern kmain

section .bss
_stack_top:
    resb 8192

section .text
_start:
    mov esp, _stack_top
    call kmain

.hang:
    cli
    hlt
    jmp .hang
```=== END FILE ===