#include "paging.h"
#include "io.h"

void paging_init(void) {
    unsigned int *page_directory = (unsigned int *)0x100000;
    unsigned int *page_table = (unsigned int *)0x101000;

    for (unsigned int i = 0; i < 1024; i++) {
        page_table[i] = (i << 12) | 3;
    }

    page_directory[0] = (unsigned int)page_table | 3;

    __asm__ volatile("movl %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    __asm__ volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    __asm__ volatile("movl %0, %%cr0" :: "r"(cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;
    unsigned int *page_table = (unsigned int *)(0xFFC00000 + (pd_index << 12));

    page_table[pt_index] = phys | flags;
    __asm__ volatile("invlpg (%0)" :: "r"(virt));
}