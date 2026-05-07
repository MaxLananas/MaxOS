#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    outb(0x21, 0xFD);
    outb(0xA1, 0xFF);
}

char keyboard_getchar(void) {
    return 0;
}

void keyboard_handler(void) {
}