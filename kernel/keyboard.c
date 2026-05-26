#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

void keyboard_callback(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        screen_putchar(scancode, 0x0F);
    }
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_callback);
}