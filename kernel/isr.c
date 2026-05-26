#include "isr.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

extern void isr0();
extern void isr1();
extern void isr2();
extern void isr3();
extern void isr4();
extern void isr5();
extern void isr6();
extern void isr7();
extern void isr8();
extern void isr9();
extern void isr10();
extern void isr11();
extern void isr12();
extern void isr13();
extern void isr14();
extern void isr15();
extern void isr16();
extern void isr17();
extern void isr18();
extern void isr19();
extern void isr20();
extern void isr21();
extern void isr22();
extern void isr23();
extern void isr24();
extern void isr25();
extern void isr26();
extern void isr27();
extern void isr28();
extern void isr29();
extern void isr30();
extern void isr31();

void *isr_routines[32] = {0};

void isr_install_handler(unsigned int isr, void (*handler)(unsigned int, unsigned int)) {
    isr_routines[isr] = handler;
    idt_set_gate(isr, (unsigned int)isr0 + isr * 4, 0x08, 0x8E);
}

void isr_uninstall_handler(unsigned int isr) {
    isr_routines[isr] = 0;
    idt_set_gate(isr, (unsigned int)isr0 + isr * 4, 0x08, 0x8E);
}

void isr_init(void) {
    for (unsigned int i = 0; i < 32; i++) {
        isr_install_handler(i, 0);
    }
}