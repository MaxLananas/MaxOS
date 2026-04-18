[BITS 32]
[EXTERN kernel_main]
global _start
_start:
    call kernel_main
    cli
    hlt