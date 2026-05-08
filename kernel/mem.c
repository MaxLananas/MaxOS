#include "mem.h"
#include "paging.h"

#define MEM_START 0x100000
#define MEM_END 0x200000

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
    paging_init();
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}