#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFD);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);

    if (scancode & 0x80) {
        // Key released
    } else {
        keyboard_buffer[buffer_pos++] = scancode;
    }

    outb(0x20, 0x20);
}

char keyboard_getchar(void) {
    if (buffer_pos > 0) {
        return keyboard_buffer[--buffer_pos];
    }
    return 0;
}