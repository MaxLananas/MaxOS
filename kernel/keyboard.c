#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

void keyboard_init(void)
{
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~(1 << 1));
}

void keyboard_handler(void)
{
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);

    if (scancode & 0x80) {
        // Key released
    } else {
        // Key pressed
        screen_putchar(scancode, 0x07);
    }

    outb(0x20, 0x20);
}