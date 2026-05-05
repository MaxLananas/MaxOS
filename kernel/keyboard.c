#include "io.h"
#include "idt.h"
#include "keyboard.h"
#include "screen.h"

extern void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
}

void keyboard_init(void) {
    irq_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
}