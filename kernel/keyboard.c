#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char key_buffer[256];
static unsigned int key_pos = 0;

void keyboard_init(void) {
    screen_writeln("Keyboard initialized", 0x0A);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while (1) {
        if (inb(KEYBOARD_STATUS_PORT) & 0x01) {
            scancode = inb(KEYBOARD_DATA_PORT);
            if (scancode < 128) {
                return scancode;
            }
        }
    }
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        key_buffer[key_pos++] = scancode;
    }
}