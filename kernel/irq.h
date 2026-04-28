#ifndef IRQ_H
#define IRQ_H

struct regs {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
};

void register_interrupt_handler(unsigned char n, void (*handler)(struct regs *r));
void irq_install_handler(unsigned char irq, void (*handler)(struct regs *r));
void irq_uninstall_handler(unsigned char irq);
void irq_remap(void);
void irq_init(void);

#endif