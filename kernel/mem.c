#include "mem.h"
#include "screen.h"

#define MEM_START 0x100000
#define MEM_END 0x200000

static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    used_pages = 0;
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}