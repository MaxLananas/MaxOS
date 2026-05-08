#include "paging.h"
#include "io.h"

unsigned int *page_directory = (unsigned int *)0x9C000;
unsigned int *page_table = (unsigned int *)0x9D000;

void paging_init(void) {
    for (unsigned int i = 0; i < 1024; i++) {
        page_table[i] = (i * 0x1000) | 3;
    }

    page_directory[0] = (unsigned int)page_table | 3;
    for (unsigned int i = 1; i < 1024; i++) {
        page_directory[i] = 0 | 2;
    }

    __asm__ volatile("movl %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    __asm__ volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    __asm__ volatile("movl %0, %%cr0" :: "r"(cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!(page_directory[pd_index] & 1)) {
        page_directory[pd_index] = (unsigned int)page_table | 3;
    }

    unsigned int *pt = (unsigned int *)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = phys | flags;
}