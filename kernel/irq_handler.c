#include "irq.h"
#include "../kernel/io.h"
#include "../drivers/screen.h"

void timer_handler(void) {
    static unsigned int tick = 0;
    tick++;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar('K', 0x0F);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if(status & 0x01) {
        unsigned char data = inb(0x60);
        screen_putchar('M', 0x0F);
    }
}

void irq_handler_init(void) {
    irq_install_handler(0, timer_handler);
    irq_install_handler(1, keyboard_handler);
    irq_install_handler(12, mouse_handler);
}