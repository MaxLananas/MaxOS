#ifndef IRQ_H
#define IRQ_H

typedef void (*irq_handler_t)(struct regs *r);

void irq_init(void);
void irq_set_handler(unsigned char irq, irq_handler_t handler);
void irq_install_handler(unsigned char irq, irq_handler_t handler);
void irq_uninstall_handler(unsigned char irq);

#endif