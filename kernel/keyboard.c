#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char key_buffer[256];
static unsigned int key_count = 0;

void keyboard_init() {
    irq_init();
}

char keyboard_getchar() {
    if (key_count == 0) {
        return 0;
    }

    char c = key_buffer[0];
    for (unsigned int i = 0; i < key_count - 1; i++) {
        key_buffer[i] = key_buffer[i + 1];
    }
    key_count--;
    return c;
}

void keyboard_handler() {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        if (key_count < 255) {
            key_buffer[key_count++] = scancode;
        }
    }
}