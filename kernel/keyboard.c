#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"
#include "idt.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_callback(struct regs *r) {
    unsigned char scancode = inb(0x60);

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        keyboard_buffer[buffer_pos++] = scancode;
    }
}

void keyboard_init(void) {
    irq_set_handler(1, keyboard_callback);
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    if (buffer_pos > 0) {
        char c = keyboard_buffer[0];
        for (unsigned int i = 0; i < buffer_pos - 1; i++) {
            keyboard_buffer[i] = keyboard_buffer[i + 1];
        }
        buffer_pos--;
        return c;
    }
    return 0;
}