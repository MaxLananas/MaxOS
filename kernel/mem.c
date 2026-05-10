#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define MAX_PAGES 1024

unsigned char page_bitmap[MAX_PAGES / 8];

void mem_init(unsigned int mem_size_kb) {
    unsigned int total_pages = mem_size_kb * 1024 / PAGE_SIZE;
    for (unsigned int i = 0; i < total_pages / 8; i++) {
        page_bitmap[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    page_bitmap[page / 8] &= ~(1 << (page % 8));
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (unsigned int i = 0; i < MAX_PAGES / 8; i++) {
        unsigned char byte = page_bitmap[i];
        while (byte) {
            count += byte & 1;
            byte >>= 1;
        }
    }
    return count;
}