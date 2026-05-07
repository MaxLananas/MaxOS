#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while (!(inb(0x64) & 1));
    scancode = inb(0x60);
    if (scancode & 0x80) {
        return 0;
    }
    return scancode;
}