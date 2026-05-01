#include "memory.h"
#include "screen.h"

unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    used_pages = 0;
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}