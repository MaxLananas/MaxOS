#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int err) {
    screen_writeln("Page fault (error code: 0x", 0x0C);
    screen_putchar("0123456789ABCDEF"[(err >> 4) & 0xF], 0x0C);
    screen_putchar("0123456789ABCDEF"[err & 0xF], 0x0C);
    screen_writeln(")", 0x0C);
    for(;;);
}