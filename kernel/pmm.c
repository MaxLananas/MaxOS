#include "pmm.h"
#include "io.h"

#define PMM_BLOCKS 1024

static unsigned int bitmap[PMM_BLOCKS / 32];

void mem_init(unsigned int mem_size_kb) {
    for (unsigned int i = 0; i < PMM_BLOCKS / 32; i++) {
        bitmap[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int index = (unsigned int)addr / 4096;
    bitmap[index / 32] &= ~(1 << (index % 32));
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (unsigned int i = 0; i < PMM_BLOCKS / 32; i++) {
        count += __builtin_popcount(bitmap[i]);
    }
    return count;
}