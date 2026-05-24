#include "mouse.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

static unsigned char mouse_cycle = 0;
static char mouse_byte[3];

void mouse_callback(unsigned int irq) {
    unsigned char data = inb(MOUSE_DATA_PORT);
    switch (mouse_cycle) {
        case 0:
            mouse_byte[0] = data;
            mouse_cycle++;
            break;
        case 1:
            mouse_byte[1] = data;
            mouse_cycle++;
            break;
        case 2:
            mouse_byte[2] = data;
            mouse_cycle = 0;
            break;
    }
}

void mouse_init(void) {
    idt_set_gate(44, (unsigned int)irq12, 0x08, 0x8E);
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
}