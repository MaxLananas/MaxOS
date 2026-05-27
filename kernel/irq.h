#ifndef IRQ_H
#define IRQ_H

void irq_set_handler(unsigned char irq, void (*handler)(void));
void irq_uninstall_handler(unsigned char irq);
void irq_init(void);

#endif