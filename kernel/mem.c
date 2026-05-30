#include "mem.h"
#include "screen.h"

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
    used_pages = 0;
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages() {
    return used_pages;
}