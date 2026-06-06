#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void keyboard_init(void) {
    irq_install_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = keyboard_getchar();

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        screen_putchar(scancode, 0x0F);
    }

    outb(0x20, 0x20);
}