#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

unsigned char mouse_cycle = 0;
char mouse_byte[3];

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
    irq_set_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char data = inb(0x60);

    switch(mouse_cycle) {
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

            if(mouse_byte[0] & 0x80 || mouse_byte[0] & 0x40) {
                break;
            }

            int x = mouse_byte[1];
            int y = mouse_byte[2];

            if(mouse_byte[0] & 0x10) {
                x |= 0xFFFFFF00;
            }
            if(mouse_byte[0] & 0x20) {
                y |= 0xFFFFFF00;
            }

            y = -y;

            screen_putchar('M', 0x0F);
            break;
    }

    outb(0x20, 0x20);
}