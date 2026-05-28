#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define MEM_START 0x100000

unsigned int used_pages = 0;
unsigned char *page_bitmap = (unsigned char*)0x1000;

void mem_init(unsigned int mem_size_kb) {
    unsigned int total_pages = mem_size_kb * 1024 / PAGE_SIZE;
    for (unsigned int i = 0; i < (total_pages + 7) / 8; i++) {
        page_bitmap[i] = 0;
    }
    used_pages = 0;
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    if (page < 1024 * 1024 / PAGE_SIZE) {
        page_bitmap[page / 8] &= ~(1 << (page % 8));
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}