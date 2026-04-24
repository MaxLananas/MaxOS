#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    outb(0x64, 0x60);
    outb(0x60, status | 1);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar('K', 0x0F);
}