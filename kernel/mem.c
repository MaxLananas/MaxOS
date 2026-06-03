#include "mem.h"
#include "screen.h"

#define MEMORY_MAP_ADDR 0x1000

void mem_init(unsigned int mem_size_kb) {
    unsigned int *memory_map = (unsigned int *)MEMORY_MAP_ADDR;
    for (unsigned int i = 0; i < mem_size_kb / 4; i++) {
        memory_map[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / 4096;
    unsigned int *memory_map = (unsigned int *)MEMORY_MAP_ADDR;
    memory_map[page / 32] &= ~(1 << (page % 32));
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    unsigned int *memory_map = (unsigned int *)MEMORY_MAP_ADDR;
    for (unsigned int i = 0; i < 1024; i++) {
        unsigned int value = memory_map[i];
        while (value) {
            count += value & 1;
            value >>= 1;
        }
    }
    return count;
}