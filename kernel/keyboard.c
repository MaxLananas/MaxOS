#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"
#include "isr.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        keyboard_buffer[buffer_pos++] = scancode;
        if (buffer_pos >= sizeof(keyboard_buffer)) {
            buffer_pos = 0;
        }
    }
}

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    idt_load(&idt_ptr);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) {
        return 0;
    }

    char c = keyboard_buffer[0];
    for (unsigned int i = 1; i < buffer_pos; i++) {
        keyboard_buffer[i-1] = keyboard_buffer[i];
    }
    buffer_pos--;
    return c;
}