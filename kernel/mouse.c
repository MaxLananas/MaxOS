#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_init(void) {
    irq_set_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char data = inb(0x60);
    screen_putchar('M', 0x0F);
}