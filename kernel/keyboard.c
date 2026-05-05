#include "keyboard.h"
#include "io.h"
#include "screen.h"

extern void keyboard_handler(void);

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while ((scancode = inb(0x64)) & 0x01) {
        unsigned char key = inb(0x60);
        if (key < 0x80) {
            return key;
        }
    }
    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 0x80) {
        screen_putchar(scancode, 0x0F);
    }
    outb(0x20, 0x20);
}