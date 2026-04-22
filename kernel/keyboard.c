#include "kernel/keyboard.h"
#include "kernel/io.h"
#include "drivers/screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8',
    '9', '0', '-', '=', '\b', '\t', 'q', 'w', 'e', 'r',
    't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', 0,
    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';',
    '\'', '`', 0, '\\', 'z', 'x', 'c', 'v', 'b', 'n',
    'm', ',', '.', '/', 0, '*', 0, ' ', 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', 0, 0, 0, '+', 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    unsigned char status;
    char keycode;

    status = inb(KEYBOARD_STATUS_PORT);
    if (status & 0x01) {
        keycode = inb(KEYBOARD_DATA_PORT);
        if (keycode < 128) {
            return keyboard_map[keycode];
        }
    }
    return 0;
}

void keyboard_handler(void) {
    char c = keyboard_getchar();
    if (c) {
        screen_putchar(c, 0x0F);
    }
}