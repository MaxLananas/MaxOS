#ifndef FAULT_HANDLER_H
#define FAULT_HANDLER_H

typedef struct {
    unsigned int ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
} registers_t;

void fault_handler(registers_t regs);

#endif