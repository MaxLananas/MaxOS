#include "paging.h"
#include "io.h"

void paging_init(void) {
    unsigned int *page_directory = (unsigned int *)0x9C000;
    unsigned int *page_table = (unsigned int *)0x9D000;

    for (unsigned int i = 0; i < 1024; i++) {
        page_table[i] = (i << 12) | 3;
    }

    page_directory[0] = (unsigned int)page_table | 3;
    page_directory[768] = (unsigned int)page_table | 3;

    __asm__ __volatile__("movl %0, %%cr3" : : "r" (page_directory));
    unsigned int cr0;
    __asm__ __volatile__("movl %%cr0, %0" : "=r" (cr0));
    cr0 |= 0x80000000;
    __asm__ __volatile__("movl %0, %%cr0" : : "r" (cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int *page_directory = (unsigned int *)0x9C000;
    unsigned int table_idx = virt >> 22;
    unsigned int *page_table = (unsigned int *)(page_directory[table_idx] & 0xFFFFF000);

    unsigned int page_idx = (virt >> 12) & 0x3FF;
    page_table[page_idx] = phys | flags;
}