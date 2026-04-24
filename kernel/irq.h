#ifndef IRQ_H
#define IRQ_H

void irq_install_handler(unsigned char irq, void (*handler)(void));
void irq_uninstall_handler(unsigned char irq);

#endif