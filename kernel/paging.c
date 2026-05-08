#include "kernel/paging.h"
#include "kernel/io.h"
#include "kernel/mem.h"

#define PAGE_SIZE 0x1000
#define PAGE_TABLE_SIZE 1024

static unsigned int *page_directory = (unsigned int*)0x100000;
static unsigned int *page_tables = (unsigned int*)0x101000;

void paging_init() {
    for (unsigned int i = 0; i < 1024; i++) {
        page_directory[i] = 0x00000002;
    }

    for (unsigned int i = 0; i < 1024; i++) {
        page_tables[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = (unsigned int)page_tables | 3;
    page_directory[768] = (unsigned int)page_tables | 3;

    __asm__ volatile("movl %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    __asm__ volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    __asm__ volatile("movl %0, %%cr0" :: "r"(cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    unsigned int *pt = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = phys | flags;
}

void paging_unmap(unsigned int page) {
    unsigned int pd_index = page >> 22;
    unsigned int pt_index = (page >> 12) & 0x3FF;

    unsigned int *pt = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = 0;
}