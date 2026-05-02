#include "paging.h"
#include "screen.h"

void paging_init(void) {
    screen_writeln("Paging initialized", 0x0A);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    (void)virt;
    (void)phys;
    (void)flags;
}