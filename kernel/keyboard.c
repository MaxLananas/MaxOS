#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x60, 0xF4);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    char c = keyboard_getchar();
    screen_putchar(c, 0x0F);
}