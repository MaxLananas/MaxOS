#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0, '\\',
    'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ', 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, '-', 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_callback(unsigned int irq) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        // Key released
    } else {
        screen_putchar(keyboard_map[scancode], 0x0F);
    }
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_callback);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while(1) {
        scancode = inb(0x60);
        if (!(scancode & 0x80)) {
            return keyboard_map[scancode];
        }
    }
}