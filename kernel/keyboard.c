#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

static unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '+', 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    outb(0x64, 0x60);
    outb(0x60, status | 1);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }
    char c = keyboard_map[scancode];
    if (c) {
        terminal_process(&c);
    }
}

char keyboard_getchar(void) {
    return 0;
}