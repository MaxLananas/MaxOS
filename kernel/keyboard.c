#include "keyboard.h"
#include "screen.h"
#include "io.h"
#include "irq_handler.h"

void keyboard_init(void) {
    irq_set_mask(1, 0);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while ((scancode = inb(0x60)) != 0) {
        if (scancode & 0x80) {
            return 0;
        }
        return scancode;
    }
    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }
    screen_putchar(scancode, 0x0F);
}