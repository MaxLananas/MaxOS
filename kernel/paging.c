#include "paging.h"
#include "screen.h"
#include "mem.h"

#define PAGE_SIZE 4096
#define PAGE_TABLE_SIZE 1024

unsigned int *page_directory = (unsigned int*)0x2000;
unsigned int *page_tables = (unsigned int*)0x3000;

void paging_init(void) {
    for (int i = 0; i < 1024; i++) {
        page_directory[i] = 0x00000002;
    }

    for (int i = 0; i < 1024; i++) {
        page_tables[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = ((unsigned int)page_tables) | 3;
    page_directory[768] = ((unsigned int)page_tables) | 3;

    asm volatile("movl %0, %%cr3" : : "r"(page_directory));
    unsigned int cr0;
    asm volatile("movl %%cr0, %0" : "=r"(cr0));
    asm volatile("movl %0, %%cr0" : : "r"(cr0 | 0x80000000));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!(page_directory[pd_index] & 1)) {
        unsigned int *new_pt = (unsigned int*)0x4000;
        for (int i = 0; i < 1024; i++) {
            new_pt[i] = 0x00000002;
        }
        page_directory[pd_index] = ((unsigned int)new_pt) | 3;
    }

    unsigned int *pt = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = phys | flags;
}