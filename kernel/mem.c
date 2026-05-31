#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096

static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    screen_writeln("Memory initialized", 0x0F);
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}