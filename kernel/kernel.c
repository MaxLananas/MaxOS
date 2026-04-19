#include "idt.h"
#include "io.h"
#include "timer.h"
#include "memory.h"

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
extern void isr32();
extern void isr33();
extern void isr34();
extern void isr35();
extern void isr36();
extern void isr37();
extern void isr38();
extern void isr39();
extern void isr40();
extern void isr41();
extern void isr42();
extern void isr43();
extern void isr44();
extern void isr45();
extern void isr46();
extern void isr47();

void isr_handler(unsigned int isr_num) {
    if (isr_num == 32) {
        timer_handler();
    } else if (isr_num == 33) {
        extern void keyboard_handler();
        keyboard_handler();
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
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);

    outb(0x21, inb(0x21) & ~0x01);
    outb(0xA1, inb(0xA1) & ~0x02);

    asm volatile("sti");
    while(1);
}