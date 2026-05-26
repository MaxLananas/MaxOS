#ifndef ISR_H
#define ISR_H

void isr_init(void);
void isr_install_handler(unsigned int isr, void (*handler)(unsigned int, unsigned int));
void isr_uninstall_handler(unsigned int isr);

#endif