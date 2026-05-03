#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0
};

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);

    if (scancode & 0x80) {
        return;
    }

    char c = keyboard_map[scancode];
    if (c) {
        terminal_process(&c);
    }
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while (1) {
        scancode = inb(KEYBOARD_DATA_PORT);
        if (!(scancode & 0x80)) {
            return keyboard_map[scancode];
        }
    }
}