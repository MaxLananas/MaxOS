#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', 0, 0, 0, '+', 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

char keyboard_getchar(void) {
    unsigned char status;
    char keycode;

    status = inb(0x64);
    if ((status & 0x01) == 0) {
        return 0;
    }

    keycode = inb(0x60);
    if (keycode < 0) return 0;

    return keyboard_map[keycode];
}

void keyboard_handler(void) {
    char c = keyboard_getchar();
    if (c) {
        screen_putchar(c, 0x0F);
    }
}