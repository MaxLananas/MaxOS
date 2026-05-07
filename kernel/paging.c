#include "paging.h"
#include "screen.h"

void paging_init(void) {
    screen_writeln("Paging: Initializing paging subsystem...", 0x0F);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    screen_writeln("Paging: Mapping virtual address to physical", 0x0F);
}