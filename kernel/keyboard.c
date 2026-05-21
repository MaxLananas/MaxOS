#include "keyboard.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

static char key_buffer[256];
static unsigned int key_pos = 0;

void keyboard_init(void) {
    irq_set_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    if (key_pos > 0) {
        char c = key_buffer[0];
        for (unsigned int i = 0; i < key_pos - 1; i++) {
            key_buffer[i] = key_buffer[i + 1];
        }
        key_pos--;
        return c;
    }
    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        key_buffer[key_pos++] = scancode;
    }
}