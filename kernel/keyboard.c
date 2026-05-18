#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void keyboard_callback(registers_t regs) {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode, 0x0F);
}

void keyboard_init(void) {
    irq_install_handler(1, keyboard_callback);
}