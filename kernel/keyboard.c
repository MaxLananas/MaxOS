#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    // Enable keyboard interrupts
    unsigned char status = inb(KEYBOARD_STATUS_PORT);
    outb(KEYBOARD_STATUS_PORT, status | 0x01);
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
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        char c = keyboard_map[scancode];
        if (c) {
            keyboard_buffer[buffer_pos++] = c;
        }
    }
}