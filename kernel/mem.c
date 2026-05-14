#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define MEM_START 0x100000

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;
unsigned int *page_bitmap = (unsigned int *)0x10000;

void mem_init(unsigned int size_kb) {
    mem_size_kb = size_kb;
    unsigned int total_pages = size_kb * 1024 / PAGE_SIZE;
    for (unsigned int i = 0; i < (total_pages + 31) / 32; i++) {
        page_bitmap[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    if (page < (mem_size_kb * 1024 / PAGE_SIZE)) {
        page_bitmap[page / 32] &= ~(1 << (page % 32));
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}

void paging_init(void) {
    for (unsigned int i = 0; i < 1024; i++) {
        paging_map(i * 0x1000, i * 0x1000, 3);
    }
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;
    unsigned int *page_directory = (unsigned int *)0xFFFFF000;
    unsigned int *page_table = (unsigned int *)0xFFC00000;
    page_directory[pd_index] = ((unsigned int)page_table) | 1;
    page_table[pt_index] = phys | flags;
}