#ifndef IRQ_H
#define IRQ_H

struct regs {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
};

void irq_set_handler(int irq, void (*handler)(struct regs *r));
void irq_unset_handler(int irq);
void irq_init(void);
void irq_remap(void);

#endif