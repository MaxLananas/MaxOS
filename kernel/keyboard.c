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
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0
};

void keyboard_init(void) {
    irq_install_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    static unsigned char buffer[128];
    static unsigned int head = 0;
    static unsigned int tail = 0;

    if (head == tail) return 0;

    unsigned char c = buffer[tail];
    tail = (tail + 1) % 128;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        buffer[head] = keyboard_map[scancode];
        head = (head + 1) % 128;
    }
}