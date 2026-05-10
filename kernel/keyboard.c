#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }
    screen_putchar(scancode, 0x0F);
    outb(0x20, 0x20);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    do {
        scancode = inb(0x60);
    } while (scancode & 0x80);
    return scancode;
}