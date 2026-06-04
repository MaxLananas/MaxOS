#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void keyboard_init(void) {
    irq_set_gate(1, (unsigned int)irq1, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        screen_putchar(scancode + '0', 0x0F);
    }
    outb(0x20, 0x20);
}