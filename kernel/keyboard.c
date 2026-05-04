#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

#define KEYBOARD_DATA_PORT 0x60

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    screen_writeln("Keyboard initialized", 0x0A);
}

char keyboard_getchar(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode & 0x80) {
        return 0;
    }
    return scancode;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        char c = keyboard_map[scancode];
        if (c) {
            keyboard_buffer[buffer_pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}