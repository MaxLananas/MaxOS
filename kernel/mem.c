[code]
#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define MEM_START 0x100000

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;
unsigned int *page_bitmap = (unsigned int*)MEM_START;

void mem_init(unsigned int size_kb) {
    mem_size_kb = size_kb;
    unsigned int total_pages = size_kb * 1024 / PAGE_SIZE;

    for (unsigned int i = 0; i < total_pages / 32; i++) {
        page_bitmap[i] = 0;
    }

    used_pages = 0;
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    if (page < mem_size_kb * 1024 / PAGE_SIZE) {
        page_bitmap[page / 32] &= ~(1 << (page % 32));
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}

void heap_init(void *start, unsigned int size) {
    screen_writeln("Heap initialized", 0x0F);
}

void heap_free(void *ptr) {
    screen_writeln("Heap free", 0x0F);
}