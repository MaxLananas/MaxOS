#include "mem.h"
#include "paging.h"

#define MEM_START 0x100000
#define MEM_END 0x200000

unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    for (unsigned int i = 0; i < mem_size_kb / 4; i++) {
        paging_map(MEM_START + i * 4096, MEM_START + i * 4096, 3);
    }
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}