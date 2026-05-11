#include "mem.h"
#include "screen.h"

#define MEM_BITMAP_SIZE 128 * 1024

unsigned char mem_bitmap[MEM_BITMAP_SIZE];

void mem_init(unsigned int mem_size_kb) {
    for (unsigned int i = 0; i < MEM_BITMAP_SIZE; i++) {
        mem_bitmap[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int index = (unsigned int)addr / 4096;
    if (index < MEM_BITMAP_SIZE * 8) {
        mem_bitmap[index / 8] &= ~(1 << (index % 8));
    }
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (unsigned int i = 0; i < MEM_BITMAP_SIZE; i++) {
        unsigned char byte = mem_bitmap[i];
        while (byte) {
            count += byte & 1;
            byte >>= 1;
        }
    }
    return count;
}