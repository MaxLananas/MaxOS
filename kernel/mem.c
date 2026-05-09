#include "mem.h"

static unsigned int mem_size_kb = 0;
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}