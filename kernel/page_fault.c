#include "page_fault.h"
#include "paging.h"
#include "screen.h"
#include "fault_handler.h"

void page_fault(unsigned int addr) {
    unsigned int err = 0;
    __asm__ volatile("mov %%cr2, %0" : "=r"(err));

    screen_writeln("Page fault at address: 0x", 0x04);
    screen_putchar('0', 0x04);
    screen_putchar('x', 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 28) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 24) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 20) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 16) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 12) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 8) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[(err >> 4) & 0xF], 0x04);
    screen_putchar("0123456789ABCDEF"[err & 0xF], 0x04);
    screen_putchar('\n', 0x04);

    if (!(err & 0x1)) {
        screen_writeln("Page not present", 0x04);
    }
    if (err & 0x2) {
        screen_writeln("Write operation", 0x04);
    }
    if (err & 0x4) {
        screen_writeln("User mode", 0x04);
    }
    if (err & 0x8) {
        screen_writeln("Reserved bits overwritten", 0x04);
    }
    if (err & 0x10) {
        screen_writeln("Instruction fetch", 0x04);
    }

    while(1);
}