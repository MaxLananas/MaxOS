#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_init(void) {
    screen_writeln("Mouse initialized", 0x0D);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
        screen_putchar('M', 0x0E);
    }
}