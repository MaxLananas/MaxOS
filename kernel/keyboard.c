#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_callback(struct regs *r) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }
    keyboard_buffer[buffer_pos++] = scancode;
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_callback);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) {
        return 0;
    }
    char c = keyboard_buffer[0];
    for (unsigned int i = 1; i < buffer_pos; i++) {
        keyboard_buffer[i - 1] = keyboard_buffer[i];
    }
    buffer_pos--;
    return c;
}