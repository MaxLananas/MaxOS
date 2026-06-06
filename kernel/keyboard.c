#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    return inb(KEYBOARD_DATA_PORT);
}

void keyboard_handler(void) {
    unsigned char scancode = keyboard_getchar();

    if (scancode < 0x80) {
        char c = keyboard_map[scancode];
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}