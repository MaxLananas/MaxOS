#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x60, 0xF4);
}

char keyboard_getchar(void) {
    unsigned char status;
    char keycode;

    status = inb(0x64);
    if (status & 0x01) {
        keycode = inb(0x60);
        if (keycode < 0x80) {
            return keycode;
        }
    }
    return 0;
}