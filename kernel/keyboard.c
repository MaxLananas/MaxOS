#include "keyboard.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
    idt_load(&idt_ptr);
}

char keyboard_getchar(void) {
    return inb(0x60);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    screen_putchar(scancode, 0x0F);
}