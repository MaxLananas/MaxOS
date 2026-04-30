#include "page_fault.h"
#include "fault_handler.h"
#include "screen.h"

void page_fault_handler(unsigned int err) {
    unsigned int fault_addr;
    __asm__ volatile("mov %%cr2, %0" : "=r"(fault_addr));

    screen_set_color(0x0C);
    screen_writeln("Page fault at address: ", 0x0C);
    screen_putchar('0' + (fault_addr >> 24) & 0xFF, 0x0C);
    screen_putchar('0' + (fault_addr >> 16) & 0xFF, 0x0C);
    screen_putchar('0' + (fault_addr >> 8) & 0xFF, 0x0C);
    screen_putchar('0' + fault_addr & 0xFF, 0x0C);
    screen_writeln("", 0x0C);

    while (1) {
        __asm__ volatile("hlt");
    }
}