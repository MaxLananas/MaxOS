#include "io.h"
#include "keyboard.h"
#include "screen.h"

static char keyboard_map[128] = {
    0, 27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', 0, 0, 0, '+', 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
}

char keyboard_getchar(void) {
    return 0;
}

void keyboard_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char keycode = inb(0x60);
        if (keycode < 128) {
            screen_putchar(keyboard_map[keycode], 0x0F);
        }
    }
}