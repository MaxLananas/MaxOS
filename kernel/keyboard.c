#include "keyboard.h"
#include "io.h"
#include "screen.h"

void keyboard_handler();

void keyboard_init() {
    outb(0x21, 0xFD);
    outb(0xA1, 0xFF);
}

char keyboard_getchar() {
    return 0;
}