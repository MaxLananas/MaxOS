#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
    screen_putchar('M', 0x0F);
}