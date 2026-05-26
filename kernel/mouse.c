#include "mouse.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

void mouse_callback(void) {
    unsigned char mouse_data = inb(0x60);
    screen_putchar('M', 0x0F);
}

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    irq_install_handler(12, mouse_callback);
}