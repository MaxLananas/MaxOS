#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }

    char c = 0;
    switch (scancode) {
        case 0x1E: c = 'a'; break;
        case 0x30: c = 'b'; break;
        case 0x2E: c = 'c'; break;
        case 0x20: c = 'd'; break;
        case 0x12: c = 'e'; break;
        case 0x21: c = 'f'; break;
        case 0x22: c = 'g'; break;
        case 0x23: c = 'h'; break;
        case 0x17: c = 'i'; break;
        case 0x24: c = 'j'; break;
        case 0x25: c = 'k'; break;
        case 0x26: c = 'l'; break;
        case 0x32: c = 'm'; break;
        case 0x31: c = 'n'; break;
        case 0x18: c = 'o'; break;
        case 0x19: c = 'p'; break;
        case 0x10: c = 'q'; break;
        case 0x13: c = 'r'; break;
        case 0x1F: c = 's'; break;
        case 0x14: c = 't'; break;
        case 0x16: c = 'u'; break;
        case 0x2F: c = 'v'; break;
        case 0x11: c = 'w'; break;
        case 0x2D: c = 'x'; break;
        case 0x15: c = 'y'; break;
        case 0x2C: c = 'z'; break;
        case 0x02: c = '1'; break;
        case 0x03: c = '2'; break;
        case 0x04: c = '3'; break;
        case 0x05: c = '4'; break;
        case 0x06: c = '5'; break;
        case 0x07: c = '6'; break;
        case 0x08: c = '7'; break;
        case 0x09: c = '8'; break;
        case 0x0A: c = '9'; break;
        case 0x0B: c = '0'; break;
        case 0x1C: c = '\n'; break;
        case 0x39: c = ' '; break;
    }

    if (c) {
        keyboard_buffer[buffer_pos++] = c;
        screen_putchar(c, 0x0F);
    }
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_handler);
}