#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_init() {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

void keyboard_handler() {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode, 0x0F);
}