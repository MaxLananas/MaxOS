#include "keyboard.h"
#include "../kernel/idt.h"
#include "../kernel/io.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static unsigned char keyboard_buffer[256];
static unsigned int keyboard_buffer_pos = 0;

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFD);
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
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        keyboard_buffer[keyboard_buffer_pos++] = scancode;
    }
}