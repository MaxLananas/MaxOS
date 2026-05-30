#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096

unsigned int mem_used = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_used = 0;
}

void mem_free_page(void *addr) {
    mem_used--;
}

unsigned int mem_used_pages(void) {
    return mem_used;
}