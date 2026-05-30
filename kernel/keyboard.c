#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

extern void keyboard_handler(void);

void keyboard_init(void) {
    irq_install_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        screen_putchar(scancode + '0', 0x0A);
    }
}