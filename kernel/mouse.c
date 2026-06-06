#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x21, inb(0x21) & 0xFD);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
        screen_putchar('M', 0x0F);
    }
}