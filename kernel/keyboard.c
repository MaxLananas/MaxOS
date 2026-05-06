#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '+', 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    irq_set_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    static char buffer[256];
    static unsigned int buffer_pos = 0;
    static unsigned int buffer_size = 0;

    if (buffer_size > 0) {
        char c = buffer[0];
        for (unsigned int i = 1; i < buffer_size; i++) {
            buffer[i - 1] = buffer[i];
        }
        buffer_size--;
        return c;
    }

    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);

    if (scancode & 0x80) {
        return;
    }

    if (buffer_size < 256) {
        buffer[buffer_size++] = keyboard_map[scancode];
    }
}