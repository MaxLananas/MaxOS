#include "kernel/io.h"
#include "kernel/keyboard.h"
#include "kernel/irq.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x60, 0xF4);
    register_interrupt_handler(33, keyboard_handler);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
}