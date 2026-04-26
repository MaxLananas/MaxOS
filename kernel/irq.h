#ifndef IRQ_H
#define IRQ_H

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);
void irq_install_handler(int irq, void (*handler)(void));
void irq_uninstall_handler(int irq);
void irq_remap(void);

#endif