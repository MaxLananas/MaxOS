#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    irq_set_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) {
        return 0;
    }

    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < buffer_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    buffer_pos--;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }

    char c = 0;
    switch (scancode) {
        case 0x1C: c = '\n'; break;
        case 0x0E: c = '\b'; break;
        default:
            if (scancode < 0x3A) {
                static const char keymap[] = {
                    0, 0, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 0, 0,
                    'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n', 0,
                    'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
                    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, 0, 0, ' '
                };
                c = keymap[scancode];
            }
    }

    if (c) {
        if (buffer_pos < 255) {
            keyboard_buffer[buffer_pos++] = c;
        }
    }
}