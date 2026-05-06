#ifndef IRQ_H
#define IRQ_H

void irq_init(void);
void irq_install_handler(int irq, void (*handler)(void));
void irq_uninstall_handler(int irq);

#endif