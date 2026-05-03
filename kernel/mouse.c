#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq_handler.h"

unsigned char mouse_cycle = 0;
char mouse_byte[3];

void mouse_wait(unsigned char a_type) {
    unsigned int timeout = 100000;
    if (!a_type) {
        while (--timeout && (inb(0x64) & 0x01));
    } else {
        while (--timeout && (inb(0x64) & 0x02));
    }
}

void mouse_write(unsigned char a_write) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, a_write);
}

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(0x60);
}

void mouse_init(void) {
    mouse_wait(1);
    outb(0x64, 0xA8);
    mouse_wait(1);
    outb(0x64, 0x20);
    mouse_wait(0);
    unsigned char status = inb(0x60) | 2;
    mouse_wait(1);
    outb(0x64, 0x60);
    mouse_wait(1);
    outb(0x60, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
    irq_init();
    idt_set_gate(44, (unsigned int)irq12, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        mouse_byte[mouse_cycle++] = inb(0x60);
        if (mouse_cycle == 3) {
            mouse_cycle = 0;
            screen_putchar('M', 0x07);
        }
    }
}