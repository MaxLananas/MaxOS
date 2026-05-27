#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

void keyboard_init(void) {
    irq_set_handler(1, keyboard_handler);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode + '0', 0x0F);
}