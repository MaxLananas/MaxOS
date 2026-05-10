#include "mem.h"
#include "io.h"

#define MEM_START 0x100000
#define MEM_END 0x200000
#define PAGE_SIZE 4096

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;
unsigned int *page_bitmap = (unsigned int *)0x10000;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
    unsigned int total_pages = (MEM_END - MEM_START) / PAGE_SIZE;
    for (unsigned int i = 0; i < (total_pages / 32); i++) {
        page_bitmap[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int page = ((unsigned int)addr - MEM_START) / PAGE_SIZE;
    page_bitmap[page / 32] &= ~(1 << (page % 32));
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}