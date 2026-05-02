#include "kernel/memory.h"

#define MEMORY_SIZE 1024 * 1024

static unsigned char memory[MEMORY_SIZE];
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    for (int i = 0; i < MEMORY_SIZE; i++) {
        memory[i] = 0;
    }
    used_pages = 0;
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / 4096;
    if (page < MEMORY_SIZE / 4096) {
        memory[page] = 0;
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}

void heap_init(void *start, unsigned int size) {
    for (int i = 0; i < size; i++) {
        ((unsigned char *)start)[i] = 0;
    }
}

void heap_free(void *ptr) {
    // Simple free implementation
}