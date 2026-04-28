#include "io.h"
#include "irq.h"
#include "mouse.h"
#include "screen.h"

unsigned char mouse_cycle = 0;
char mouse_byte[3];
unsigned char mouse_x = 0;
unsigned char mouse_y = 0;

void mouse_wait(unsigned char a_type) {
    unsigned int _time_out=100000;
    if(a_type==0) {
        while(_time_out--) {
            if((inb(0x64) & 1)==1) {
                return;
            }
        }
        return;
    } else {
        while(_time_out--) {
            if((inb(0x64) & 2)==0) {
                return;
            }
        }
        return;
    }
}

void mouse_write(unsigned char a_write) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, a_write);
}

unsigned char mouse_read() {
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

    register_interrupt_handler(44, mouse_handler);
}

void mouse_handler(struct regs *r) {
    unsigned char status = inb(0x64);
    if ((status & 0x20) == 0) {
        return;
    }

    mouse_byte[mouse_cycle] = inb(0x60);
    mouse_cycle++;

    if (mouse_cycle == 3) {
        mouse_cycle = 0;

        signed char movement_x = mouse_byte[1];
        signed char movement_y = mouse_byte[2];

        mouse_x += movement_x;
        mouse_y += movement_y;

        screen_putchar('M', 0x07);
    }
}