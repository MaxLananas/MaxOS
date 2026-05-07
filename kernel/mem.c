#include "mem.h"
#include "screen.h"

#define MEM_BITMAP_SIZE 128

static unsigned int mem_bitmap[MEM_BITMAP_SIZE];
static unsigned int total_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    total_pages = mem_size_kb / 4;
    for (int i = 0; i < MEM_BITMAP_SIZE; i++) {
        mem_bitmap[i] = 0;
    }
}

void *mem_alloc_page(void) {
    for (unsigned int i = 0; i < total_pages / 32; i++) {
        if (mem_bitmap[i] != 0xFFFFFFFF) {
            for (int j = 0; j < 32; j++) {
                if (!(mem_bitmap[i] & (1 << j))) {
                    mem_bitmap[i] |= (1 << j);
                    return (void*)((i * 32 + j) * 4096);
                }
            }
        }
    }
    return 0;
}

void mem_free_page(void *addr) {
    unsigned int index = (unsigned int)addr / 4096;
    mem_bitmap[index / 32] &= ~(1 << (index % 32));
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (int i = 0; i < total_pages / 32; i++) {
        unsigned int val = mem_bitmap[i];
        while (val) {
            count += val & 1;
            val >>= 1;
        }
    }
    return count;
}