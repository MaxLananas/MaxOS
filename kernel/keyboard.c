#include "keyboard.h"
#include "io.h"
#include "screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 1;
    outb(0x64, 0x60);
    outb(0x60, status);
}

char keyboard_getchar(void) {
    if (inb(KEYBOARD_STATUS_PORT) & 0x01) {
        unsigned char scancode = inb(KEYBOARD_DATA_PORT);
        if (scancode < 128) {
            return keyboard_map[scancode];
        }
    }
    return 0;
}

void keyboard_handler(void) {
    keyboard_getchar();
}