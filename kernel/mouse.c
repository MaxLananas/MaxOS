#include "drivers/screen.h"
#include "kernel/io.h"
#include "kernel/idt.h"
#include "kernel/mouse.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

void mouse_init(void) {
    outb(MOUSE_COMMAND_PORT, 0xA8);
    outb(MOUSE_COMMAND_PORT, 0x20);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    outb(MOUSE_COMMAND_PORT, 0x60);
    outb(MOUSE_DATA_PORT, status);
    outb(MOUSE_COMMAND_PORT, 0xD4);
    outb(MOUSE_DATA_PORT, 0xF4);
    inb(MOUSE_DATA_PORT);

    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xEF);
}

void mouse_handler(void) {
    unsigned char mouse_data = inb(MOUSE_DATA_PORT);
    screen_putchar('M', 0x0A);
    outb(0x20, 0x20);
}