#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)keyboard_handler, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = keyboard_getchar();
    screen_putchar(scancode, 0x0F);
}