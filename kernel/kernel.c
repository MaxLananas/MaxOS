#include "idt.h"
#include "io.h"
#include "timer.h"
#include "memory.h"

void isr_handler(unsigned int isr_num) {
    if (isr_num == 32) {
        timer_handler();
    } else {
        outb(0x20, 0x20);
        if (isr_num >= 40) outb(0xA0, 0x20);
    }
}

void kmain(void) {
    idt_init();
    unsigned int i;
    for (i = 0; i < IDT_ENTRIES; i++) {
        idt_set_gate(i, (unsigned int)isr0 + i * 8, 0x08, 0x8E);
    }

    timer_init();
    mem_init(0x100000, 0x200000);

    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~0x01);

    asm volatile("sti");
    while(1);
}