#include "paging.h"
#include "io.h"

void paging_init(void) {
    // Simple identity mapping for first 4MB
    for (unsigned int i = 0; i < 1024; i++) {
        unsigned int *page_table = (unsigned int*)(0x1000 + i * 0x1000);
        for (unsigned int j = 0; j < 1024; j++) {
            page_table[j] = (i * 1024 + j) * 0x1000 | 3;
        }
    }
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;
    unsigned int *page_table = (unsigned int*)(0x1000 + pd_index * 0x1000);
    page_table[pt_index] = phys | flags;
}