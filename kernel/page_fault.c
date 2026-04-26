#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int err) {
    screen_writeln("Page fault handler", 0x0C);
}