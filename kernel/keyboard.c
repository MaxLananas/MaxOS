#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"
#include "terminal.h"

void keyboard_init(void) {
    outb(0x21, inb(0x21) & ~(1 << 1));
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while ((scancode = inb(0x60)) == 0);
    return scancode;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        char c = scancode;
        screen_putchar(c, 0x0F);
    }
}