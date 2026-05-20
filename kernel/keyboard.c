#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    status |= 1;
    outb(0x64, 0x60);
    outb(0x60, status);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = keyboard_getchar();
    (void)scancode;
}