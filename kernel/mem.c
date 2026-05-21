#include "mem.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define MEM_START 0x100000

static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    used_pages = 0;
}

void mem_free_page(void *addr) {
    if ((unsigned int)addr >= MEM_START) {
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}