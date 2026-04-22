#include "irq.h"
#include "idt.h"
#include "io.h"
#include "keyboard.h"
#include "timer.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 33) {
        keyboard_handler();
    }
}

void irq_init(void) {
    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    idt_set_gate(34, (unsigned int)isr34, 0x08, 0x8E);
    idt_set_gate(35, (unsigned int)isr35, 0x08, 0x8E);
    idt_set_gate(36, (unsigned int)isr36, 0x08, 0x8E);
    idt_set_gate(37, (unsigned int)isr37, 0x08, 0x8E);
    idt_set_gate(38, (unsigned int)isr38, 0x08, 0x8E);
    idt_set_gate(39, (unsigned int)isr39, 0x08, 0x8E);
    idt_set_gate(40, (unsigned int)isr40, 0x08, 0x8E);
    idt_set_gate(41, (unsigned int)isr41, 0x08, 0x8E);
    idt_set_gate(42, (unsigned int)isr42, 0x08, 0x8E);
    idt_set_gate(43, (unsigned int)isr43, 0x08, 0x8E);
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
    idt_set_gate(45, (unsigned int)isr45, 0x08, 0x8E);
    idt_set_gate(46, (unsigned int)isr46, 0x08, 0x8E);
    idt_set_gate(47, (unsigned int)isr47, 0x08, 0x8E);
}