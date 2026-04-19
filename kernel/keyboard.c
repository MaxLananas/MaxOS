#include "keyboard.h"
#include "io.h"

void keyboard_handler() {
    unsigned char scancode = inb(0x60);
    outb(0x20, 0x20);
}