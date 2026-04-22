#include "memory.h"

#define MEMORY_SIZE 1024 * 1024

static unsigned char memory[MEMORY_SIZE];
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    (void)mem_size_kb;
}

void mem_free_page(void *addr) {
    (void)addr;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}