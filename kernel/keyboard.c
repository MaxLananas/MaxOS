#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while(!(inb(KEYBOARD_STATUS_PORT) & 0x01));
    scancode = inb(KEYBOARD_DATA_PORT);
    return scancode;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if(scancode < 0x80) {
        char c = scancode;
        screen_putchar(c, 0x0F);
    }
    outb(0x20, 0x20);
}