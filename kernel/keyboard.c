#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

char keyboard_buffer[256];
unsigned int keyboard_buffer_pos = 0;

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

char keyboard_getchar(void) {
    if (keyboard_buffer_pos == 0) {
        return 0;
    }

    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < keyboard_buffer_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    keyboard_buffer_pos--;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }

    if (keyboard_buffer_pos < 255) {
        keyboard_buffer[keyboard_buffer_pos++] = scancode;
    }
}