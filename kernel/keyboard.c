#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

char keyboard_buffer[256];
unsigned int keyboard_pos = 0;

void keyboard_callback(registers_t regs) {
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        // Key released
    } else {
        keyboard_buffer[keyboard_pos++] = scancode;
    }
}

void keyboard_init(void) {
    keyboard_pos = 0;
    irq_install_handler(1, keyboard_callback);
}

char keyboard_getchar(void) {
    if (keyboard_pos > 0) {
        char c = keyboard_buffer[0];
        for (unsigned int i = 0; i < keyboard_pos - 1; i++) {
            keyboard_buffer[i] = keyboard_buffer[i + 1];
        }
        keyboard_pos--;
        return c;
    }
    return 0;
}