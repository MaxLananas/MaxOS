#include "keyboard.h"
#include "io.h"
#include "idt.h"
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
    idt_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    unsigned char status;
    char keycode;

    while ((status = inb(0x64)) & 0x01) {
        keycode = inb(0x60);
        if (keycode < 0) {
            return 0;
        }
        return keyboard_map[(unsigned char)keycode];
    }

    return 0;
}

void keyboard_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        char keycode = inb(0x60);
        if (keycode < 0) {
            return;
        }
        char c = keyboard_map[(unsigned char)keycode];
        if (c != 0) {
            screen_putchar(c, 0x07);
        }
    }
}