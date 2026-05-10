#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void mouse_init(void) {
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
    outb(0x64, 0xA8);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xF4);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    while (status & 0x01) {
        unsigned char mouse_data = inb(0x60);
        static unsigned char cycle = 0;
        static char mouse_bytes[3];
        mouse_bytes[cycle++] = mouse_data;
        if (cycle == 3) {
            cycle = 0;
            screen_putchar('M', 0x0F);
        }
        status = inb(0x64);
    }
    outb(0x20, 0x20);
}