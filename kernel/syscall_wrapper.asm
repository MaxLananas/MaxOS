[bits 32]

global syscall_handler_wrapper

syscall_handler_wrapper:
    pushl %ebp
    movl %esp, %ebp
    pushl %edi
    pushl %esi
    pushl %edx
    pushl %ecx
    pushl %ebx
    pushl %eax
    call syscall_handler
    popl %eax
    popl %ebx
    popl %ecx
    popl %edx
    popl %esi
    popl %edi
    movl %ebp, %esp
    popl %ebp
    ret