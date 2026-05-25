#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

static char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    irq_set_handler(1, keyboard_handler);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);

    if(scancode < 128) {
        char c = keyboard_map[scancode];
        if(c) {
            screen_putchar(c, 0x0F);
        }
    }

    outb(0x20, 0x20);
}

char keyboard_getchar(void) {
    char c = 0;
    while(c == 0) {
        unsigned char scancode = inb(0x60);
        if(scancode < 128) {
            c = keyboard_map[scancode];
        }
    }
    return c;
}