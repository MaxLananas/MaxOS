#ifndef IRQ_H
#define IRQ_H

extern void irq0();
extern void irq1();
extern void irq2();
extern void irq3();
extern void irq4();
extern void irq5();
extern void irq6();

void irq_handler(unsigned int num);

#endif