#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

static unsigned char mouse_byte[3];
static unsigned char mouse_cycle = 0;

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60);
    status |= 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char data = inb(0x60);
    mouse_byte[mouse_cycle] = data;

    if (mouse_cycle == 0 && !(data & 0x08)) return;

    mouse_cycle++;

    if (mouse_cycle == 3) {
        mouse_cycle = 0;
        int x = mouse_byte[1];
        int y = mouse_byte[2];
        screen_putchar('M', 0x0F);
    }
}