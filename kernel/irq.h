#ifndef IRQ_H
#define IRQ_H

void irq_install_handler(unsigned char irq, void (*handler)(void));

#endif