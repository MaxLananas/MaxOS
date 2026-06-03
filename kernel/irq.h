#ifndef IRQ_H
#define IRQ_H

void irq_install_handler(int irq, void (*handler)(void));
void irq_uninstall_handler(int irq);
void irq_remap(void);

#endif