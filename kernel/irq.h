#ifndef IRQ_H
#define IRQ_H

typedef struct {
    unsigned int ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
} registers_t;

void irq_install_handler(unsigned int irq, void (*handler)(registers_t));
void irq_uninstall_handler(unsigned int irq);
void irq_handler(registers_t regs);

#endif