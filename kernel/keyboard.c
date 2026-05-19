#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

static char keyboard_map[128] = {
    0, 27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ', 0
};

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    unsigned char status;
    while ((status = inb(0x64)) & 0x01) {
        unsigned char keycode = inb(0x60);
        if (keycode < 128) {
            return keyboard_map[keycode];
        }
    }
    return 0;
}

void keyboard_handler(void) {
    unsigned char keycode = inb(0x60);
    if (keycode < 128) {
        char c = keyboard_map[keycode];
        if (c != 0) {
            screen_putchar(c, 0x0F);
        }
    }
}