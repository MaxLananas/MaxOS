#include "io.h"
#include "keyboard.h"
#include "screen.h"

void keyboard_init(void) {
}

char keyboard_getchar(void) {
    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar('K', 0x0F);
}