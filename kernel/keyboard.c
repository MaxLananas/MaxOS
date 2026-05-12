#include "keyboard.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode, 0x0F);
}