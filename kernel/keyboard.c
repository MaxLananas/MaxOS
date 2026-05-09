#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    status |= 1;
    outb(0x64, 0x60);
    outb(0x60, status);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) return 0;
    char c = keyboard_buffer[0];
    for (unsigned int i = 1; i < buffer_pos; i++) {
        keyboard_buffer[i - 1] = keyboard_buffer[i];
    }
    buffer_pos--;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) return;

    char c = 0;
    if (scancode < 0x3A) {
        static const char keymap[] = {
            0, 27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
            '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
            0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0, '\\',
            'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ', 0
        };
        c = keymap[scancode];
    }

    if (c) {
        if (buffer_pos < 255) {
            keyboard_buffer[buffer_pos++] = c;
        }
    }
}