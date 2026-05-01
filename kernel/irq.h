#ifndef IRQ_H
#define IRQ_H

void irq_set_mask(unsigned char irq);
void irq_clear_mask(unsigned char irq);
void irq_install_handler(int irq, void (*handler)(void));
void irq_uninstall_handler(int irq);
void irq_init(void);

#endif