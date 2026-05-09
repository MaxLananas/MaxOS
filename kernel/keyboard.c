#include "kernel/io.h"
#include "kernel/keyboard.h"
#include "drivers/screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int keyboard_pos = 0;

void keyboard_init(void) {
    screen_writeln("Keyboard initialized", 0x0A);
}

char keyboard_getchar(void) {
    if (inb(KEYBOARD_STATUS_PORT) & 0x01) {
        unsigned char scancode = inb(KEYBOARD_DATA_PORT);
        if (scancode < 128) {
            return scancode;
        }
    }
    return 0;
}

void keyboard_handler(void) {
    char c = keyboard_getchar();
    if (c) {
        keyboard_buffer[keyboard_pos++] = c;
    }
}