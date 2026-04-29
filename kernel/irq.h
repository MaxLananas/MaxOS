#ifndef IRQ_H
#define IRQ_H

void (*irq_handlers[16])(void);
void irq_init(void);
void irq_install_handler(int irq, void (*handler)(void));

#endif