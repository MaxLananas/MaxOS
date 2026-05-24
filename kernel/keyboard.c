#include "keyboard.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int keyboard_pos = 0;

void keyboard_callback(unsigned int irq) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        keyboard_buffer[keyboard_pos++] = scancode;
    }
}

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    if (keyboard_pos > 0) {
        unsigned char scancode = keyboard_buffer[0];
        keyboard_pos--;
        for (unsigned int i = 0; i < keyboard_pos; i++) {
            keyboard_buffer[i] = keyboard_buffer[i+1];
        }

        if (scancode < 128) {
            return scancode;
        }
    }
    return 0;
}