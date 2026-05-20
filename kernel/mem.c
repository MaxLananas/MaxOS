#include "mem.h"
#include "screen.h"

unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    (void)mem_size_kb;
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
    (void)addr;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}