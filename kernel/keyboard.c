#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    irq_clear_mask(1);
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
    keyboard_buffer[buffer_pos++] = scancode;
}