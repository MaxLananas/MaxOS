#include "keyboard.h"
#include "screen.h"
#include "io.h"
#include "isr.h"

static char keyboard_buffer[256];
static unsigned int keyboard_pos = 0;

void keyboard_callback(struct regs *r) {
    unsigned char scancode = inb(0x60);

    if (scancode & 0x80) {
        scancode -= 0x80;
    }

    keyboard_buffer[keyboard_pos++] = scancode;
}

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    irq_install_handler(1, keyboard_callback);
}

char keyboard_getchar(void) {
    if (keyboard_pos == 0) {
        return 0;
    }

    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < keyboard_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    keyboard_pos--;

    return c;
}