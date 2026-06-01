#include "paging.h"
#include "screen.h"
#include "mem.h"

void paging_init(void) {
    paging_setup();
    screen_writeln("Paging initialized", 0x0F);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    paging_map_page(virt, phys, flags);
}