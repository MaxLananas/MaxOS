#include "keyboard.h"
#include "io.h"
#include "screen.h"

char keyboard_getchar(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return 0;
    }
    return scancode;
}