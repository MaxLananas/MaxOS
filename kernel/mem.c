#include "mem.h"

#define MEMORY_SIZE 1024 * 1024 * 16 // 16MB
static unsigned char memory[MEMORY_SIZE];
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    // Simple memory initialization
    for (unsigned int i = 0; i < MEMORY_SIZE; i++) {
        memory[i] = 0;
    }
    used_pages = 0;
}

void mem_free_page(void *addr) {
    // Simple page free
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}