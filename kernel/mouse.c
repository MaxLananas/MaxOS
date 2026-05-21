#include "mouse.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    status = inb(0x60) & 0xFD;
    outb(0x64, 0x60);
    outb(0x60, status);
    irq_set_handler(12, mouse_handler);
}