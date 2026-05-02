#include "memory.h"

unsigned int mem_used = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_used = 0;
}

void mem_free_page(void *addr) {
    (void)addr;
}

unsigned int mem_used_pages(void) {
    return mem_used;
}