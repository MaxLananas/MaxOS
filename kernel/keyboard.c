#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    screen_writeln("Keyboard initialized", 0x0A);
}

char keyboard_getchar(void) {
    while (1) {
        if (buffer_pos > 0) {
            char c = keyboard_buffer[0];
            for (unsigned int i = 1; i < buffer_pos; i++) {
                keyboard_buffer[i-1] = keyboard_buffer[i];
            }
            buffer_pos--;
            return c;
        }
    }
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        keyboard_buffer[buffer_pos++] = scancode;
    }
}