#ifndef IRQ_H
#define IRQ_H

typedef struct {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
} registers_t;

void irq_install_handler(unsigned char irq, void (*handler)(registers_t));
void irq_uninstall_handler(unsigned char irq);
void irq_init(void);

#endif