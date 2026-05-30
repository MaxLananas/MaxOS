#include "mem.h"

unsigned int mem_used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    // Simple memory initialization
    mem_used_pages = 0;
}

void mem_free_page(void *addr) {
    // Simple page free
    mem_used_pages--;
}

unsigned int mem_used_pages(void) {
    return mem_used_pages;
}