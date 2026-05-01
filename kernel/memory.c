#include "memory.h"
#include "screen.h"

void mem_init(unsigned int mem_size_kb) {
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
}

unsigned int mem_used_pages(void) {
    return 0;
}