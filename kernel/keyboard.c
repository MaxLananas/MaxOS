#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) return 0;
    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < buffer_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    buffer_pos--;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        keyboard_buffer[buffer_pos++] = scancode;
    }
    outb(0x20, 0x20);
}