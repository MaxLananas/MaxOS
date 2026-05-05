#include "../drivers/screen.h"
#include "../kernel/mouse.h"
#include "../kernel/io.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
}