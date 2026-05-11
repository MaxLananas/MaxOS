#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
        screen_putchar('M', 0x0B);
    }
}

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
    screen_writeln("Mouse initialized", 0x0A);
}