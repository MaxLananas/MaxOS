#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
    irq_clear_mask(12);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (!(status & 0x20)) {
        return;
    }
    unsigned char data = inb(0x60);
    screen_putchar('M', 0x0F);
}