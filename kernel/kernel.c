#include "idt.h"
#include "io.h"

void isr_handler(unsigned int isr_num) {
    outb(0x20, 0x20);
    if (isr_num >= 40) outb(0xA0, 0x20);
}

void kmain(void) {
    idt_init();
    unsigned int i;
    for (i = 0; i < IDT_ENTRIES; i++) {
        idt_set_gate(i, (unsigned int)isr0 + i * 8, 0x08, 0x8E);
    }
    asm volatile("sti");
    while(1);
}