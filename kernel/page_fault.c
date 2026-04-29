#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int err) {
    screen_writeln("Page fault", 0x0F);
    for(;;);
}