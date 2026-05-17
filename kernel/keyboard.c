#include "keyboard.h"
#include "idt.h"
#include "io.h"

extern void irq1();

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    // Gestion du clavier simplifiée
}