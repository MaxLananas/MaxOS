#include "keyboard.h"
#include "../kernel/io.h"
#include "pci.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64
#define KEYBOARD_IRQ 1

static unsigned char kb_buffer[256];
static unsigned int kb_buffer_start = 0;
static unsigned int kb_buffer_end = 0;

void kb_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    status |= 1;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x61, 0x01);
}

unsigned char kb_haskey(void) {
    return kb_buffer_start != kb_buffer_end;
}

char kb_getchar(void) {
    if (!kb_haskey()) {
        return 0;
    }
    char c = kb_buffer[kb_buffer_start];
    kb_buffer_start = (kb_buffer_start + 1) % 256;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode & 0x80) {
        return;
    }

    if (scancode == 0x0E) {
        if (kb_buffer_end != (kb_buffer_start - 1) % 256) {
            kb_buffer[kb_buffer_end] = '\b';
            kb_buffer_end = (kb_buffer_end + 1) % 256;
        }
    } else {
        char c = 0;
        if (scancode < 0x3A) {
            static const char keymap[] = {
                0, 27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
                '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
                0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
                '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ', 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-', 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0
            };
            c = keymap[scancode];
        }

        if (c && kb_buffer_end != (kb_buffer_start - 1) % 256) {
            kb_buffer[kb_buffer_end] = c;
            kb_buffer_end = (kb_buffer_end + 1) % 256;
        }
    }
}