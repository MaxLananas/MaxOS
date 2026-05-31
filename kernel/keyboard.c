#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

void keyboard_init(void)
{
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

char keyboard_getchar(void)
{
    return inb(0x60);
}

void keyboard_handler(void)
{
    unsigned char scancode = inb(0x60);
    if (scancode & 0x80) {
        return;
    }
    screen_putchar(keyboard_getchar(), 0x0F);
}