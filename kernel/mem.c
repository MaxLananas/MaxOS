#include "mem.h"

#define MEM_BITMAP_SIZE 128 * 1024

unsigned char mem_bitmap[MEM_BITMAP_SIZE];

void mem_init(unsigned int mem_size_kb) {
    for (unsigned int i = 0; i < MEM_BITMAP_SIZE; i++) {
        mem_bitmap[i] = 0;
    }
}

void *mem_alloc_page(void) {
    for (unsigned int i = 0; i < MEM_BITMAP_SIZE; i++) {
        if (mem_bitmap[i] == 0) {
            mem_bitmap[i] = 1;
            return (void*)(i * 4096);
        }
    }
    return 0;
}

void mem_free_page(void *addr) {
    unsigned int index = (unsigned int)addr / 4096;
    if (index < MEM_BITMAP_SIZE) {
        mem_bitmap[index] = 0;
    }
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (unsigned int i = 0; i < MEM_BITMAP_SIZE; i++) {
        if (mem_bitmap[i]) count++;
    }
    return count;
}