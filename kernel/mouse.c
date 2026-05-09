#include "mouse.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

void mouse_init(void) {
    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~(1 << 2));
}

void mouse_handler(void) {
    unsigned char data = inb(0x60);
    screen_putchar('M', 0x0F);
    outb(0x20, 0x20);
}