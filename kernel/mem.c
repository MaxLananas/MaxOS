#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096

unsigned int *page_directory = (unsigned int*)0x9C000;
unsigned int *page_table = (unsigned int*)0x9D000;
unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    for (int i = 0; i < 1024; i++) {
        page_table[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = (unsigned int)page_table | 3;
    for (int i = 1; i < 1024; i++) {
        page_directory[i] = 0 | 2;
    }

    __asm__ volatile("movl %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    __asm__ volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    __asm__ volatile("movl %0, %%cr0" :: "r"(cr0));
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    page_table[page] = 0;
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}

void paging_init(void) {
    screen_writeln("Paging initialized", 0x0A);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!(page_directory[pd_index] & 1)) {
        unsigned int *new_pt = (unsigned int*)0x9E000;
        for (int i = 0; i < 1024; i++) {
            new_pt[i] = 0;
        }
        page_directory[pd_index] = (unsigned int)new_pt | 3;
    }

    unsigned int *pt = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    pt[pt_index] = phys | flags;
}