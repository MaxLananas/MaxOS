#include "paging.h"
#include "screen.h"

#define PAGE_SIZE 4096

void paging_init(void) {
    screen_writeln("Paging initialized", 0x0A);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    // Placeholder for actual paging implementation
}