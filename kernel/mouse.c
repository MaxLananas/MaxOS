#include "mouse.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

unsigned char mouse_cycle = 0;
char mouse_byte[3];

void mouse_callback(struct regs *r) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char mouse_in = inb(0x60);
        switch (mouse_cycle) {
            case 0:
                mouse_byte[0] = mouse_in;
                if (!(mouse_in & 0x08)) return;
                mouse_cycle++;
                break;
            case 1:
                mouse_byte[1] = mouse_in;
                mouse_cycle++;
                break;
            case 2:
                mouse_byte[2] = mouse_in;
                screen_putchar('M', 0x0F);
                mouse_cycle = 0;
                break;
        }
    }
}

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    register_interrupt_handler(IRQ12, &mouse_callback);
}