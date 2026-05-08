#include "mem.h"
#include "screen.h"

void mem_init(unsigned int mem_size_kb) {
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
    // Placeholder for memory free implementation
}

unsigned int mem_used_pages(void) {
    return 0;
}