#include "paging.h"
#include "screen.h"

#define PAGE_SIZE 4096

unsigned int page_directory[1024] __attribute__((aligned(4096)));
unsigned int page_table[1024] __attribute__((aligned(4096)));

void paging_init(void) {
    for (unsigned int i = 0; i < 1024; i++) {
        page_table[i] = (i * PAGE_SIZE) | 3;
        page_directory[i] = ((unsigned int)page_table + (i * PAGE_SIZE)) | 3;
    }
    asm volatile("movl %0, %%cr3" : : "r" (page_directory));
    unsigned int cr0;
    asm volatile("movl %%cr0, %0" : "=r" (cr0));
    cr0 |= 0x80000000;
    asm volatile("movl %0, %%cr0" : : "r" (cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;
    page_table[pt_index] = (phys & 0xFFFFF000) | flags;
    page_directory[pd_index] = ((unsigned int)page_table + (pd_index * PAGE_SIZE)) | 3;
}