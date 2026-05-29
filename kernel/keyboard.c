#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while((scancode = inb(0x64)) & 0x01 == 0);
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode, 0x0F);
}