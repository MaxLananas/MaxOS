#ifndef ISR_H
#define ISR_H

struct regs {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
};

void isr_handler(unsigned int num, unsigned int err);
void irq_handler(unsigned int num);

#endif