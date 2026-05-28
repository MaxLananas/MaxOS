#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0
};

void keyboard_init(void) {
    irq_set_mask(1, 0);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while ((inb(0x64) & 0x01) == 0);
    scancode = inb(0x60);

    if (scancode & 0x80) {
        return 0;
    }

    return keyboard_map[scancode];
}

void keyboard_handler(void) {
    char c = keyboard_getchar();
    if (c) {
        screen_putchar(c, 0x0F);
    }
    pic_send_eoi(1);
}