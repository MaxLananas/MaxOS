#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int err) {
    screen_writeln("Page fault occurred!", 0x0C);
    while (1) {
        __asm__ volatile("hlt");
    }
}