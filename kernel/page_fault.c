#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int addr) {
    screen_writeln("Page fault at address", 0x0F);
}