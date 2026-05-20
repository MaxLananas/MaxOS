#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x64);
    status |= 0x02;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char mouse_data = inb(0x60);
    (void)mouse_data;
}