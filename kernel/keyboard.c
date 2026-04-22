#include "kernel/idt.h"
#include "kernel/io.h"

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~0x02);
}
