#ifndef IRQ_H
#define IRQ_H

struct regs {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
};

void irq_init(void);
void irq_install_handler(int irq, void (*handler)(void));
void irq_uninstall_handler(int irq);

#endif