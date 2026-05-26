#ifndef IRQ_H
#define IRQ_H

void irq_init(void);
void irq_install_handler(unsigned char irq, void (*handler)(void));
void irq_uninstall_handler(unsigned char irq);
void irq_handler(unsigned int num);

#endif