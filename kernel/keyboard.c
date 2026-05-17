#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', 0, 0, 0, '+', 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFD);
}

void keyboard_handler(void) {
    unsigned char status = inb(KEYBOARD_STATUS_PORT);
    if (status & 0x01) {
        unsigned char keycode = inb(KEYBOARD_DATA_PORT);
        if (keycode < 128) {
            char c = keyboard_map[keycode];
            if (c) {
                screen_putchar(c, 0x0F);
            }
        }
    }

    outb(0x20, 0x20);
}