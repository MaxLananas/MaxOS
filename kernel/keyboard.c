#include "keyboard.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x64) & 0xFD;
    outb(0x64, 0x60);
    outb(0x64, status);
    outb(0x60, 0xF4);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = keyboard_getchar();
    (void)scancode;
}