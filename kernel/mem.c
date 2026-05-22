#include "mem.h"
#include "screen.h"
#include "paging.h"

#define MEM_BITMAP_SIZE 128

unsigned char mem_bitmap[MEM_BITMAP_SIZE];

void mem_init(unsigned int mem_size_kb) {
    screen_writeln("Initializing memory", 0x0A);

    for (int i = 0; i < MEM_BITMAP_SIZE; i++) {
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
    for (int i = 0; i < MEM_BITMAP_SIZE; i++) {
        for (int j = 0; j < 8; j++) {
            if (mem_bitmap[i] & (1 << j)) {
                count++;
            }
        }
    }
    return count;
}