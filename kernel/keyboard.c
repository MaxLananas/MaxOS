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

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        screen_putchar(scancode, 0x0F);
    }
}

char keyboard_getchar(void) {
    unsigned char scancode;
    do {
        scancode = inb(0x60);
    } while (scancode >= 128);
    return scancode;
}