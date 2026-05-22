#include "mouse.h"
#include "io.h"
#include "idt.h"
#include "irq.h"
#include "screen.h"

static int mouse_x = 40;
static int mouse_y = 12;

void mouse_init(void) {
    outb(0x64, 0xA8); // Enable mouse
    outb(0x64, 0x20); // Read command byte
    unsigned char status = inb(0x60);
    status |= 0x02; // Enable IRQ12
    outb(0x64, 0x60); // Write command byte
    outb(0x60, status);

    outb(0x64, 0xD4); // Send to mouse
    outb(0x60, 0xF4); // Enable data reporting

    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (!(status & 0x20)) return;

    unsigned char mouse_data = inb(0x60);

    // TODO: Implement mouse movement handling
    screen_putchar('M', 0x0F);

    outb(0x20, 0x20);
    outb(0xA0, 0x20);
}