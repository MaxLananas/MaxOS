#include "mouse.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

void mouse_init(void) {
    irq_install_handler(12, mouse_handler);
    screen_writeln("Mouse initialized", 0x0F);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
    }
}