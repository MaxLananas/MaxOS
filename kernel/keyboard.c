#include "keyboard.h"
#include "irq.h"
#include "../kernel/io.h"
#include "../screen.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);

    if(scancode & 0x80) {
        // Key released
    } else {
        keyboard_buffer[buffer_pos++] = scancode;
        screen_putchar(scancode, 0x0F);
    }

    outb(0x20, 0x20);
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_handler);
    screen_writeln("KEYBOARD: Initialized", 0x02);
}

char keyboard_getchar(void) {
    if(buffer_pos > 0) {
        char c = keyboard_buffer[0];
        for(unsigned int i = 0; i < buffer_pos - 1; i++) {
            keyboard_buffer[i] = keyboard_buffer[i + 1];
        }
        buffer_pos--;
        return c;
    }
    return 0;
}