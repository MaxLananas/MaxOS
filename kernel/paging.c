#include "paging.h"
#include "screen.h"
#include "mem.h"

#define PAGE_SIZE 4096
#define PAGE_TABLE_SIZE 1024
#define PAGE_DIR_SIZE 1024

unsigned int *page_directory = (unsigned int*)0x9C000;
unsigned int *first_page_table = (unsigned int*)0x9D000;

void paging_init(void) {
    screen_writeln("Initializing paging", 0x0A);

    for (int i = 0; i < PAGE_TABLE_SIZE; i++) {
        first_page_table[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = (unsigned int)first_page_table | 3;
    for (int i = 1; i < PAGE_DIR_SIZE; i++) {
        page_directory[i] = 0 | 2;
    }

    asm volatile("movl %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    asm volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    asm volatile("movl %0, %%cr0" :: "r"(cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    unsigned int *pt = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = phys | flags;
}