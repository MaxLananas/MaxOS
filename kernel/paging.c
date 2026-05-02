#include "paging.h"
#include "memory.h"

void paging_init(void) {
    // Already initialized in mem_init
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    unsigned int *page_table = (unsigned int*)(0x101000 + pd_index * 4096);
    page_table[pt_index] = phys | flags;
}