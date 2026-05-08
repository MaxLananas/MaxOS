#include "kernel/mem.h"
#include "kernel/paging.h"

static unsigned int mem_size_kb = 0;
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
    paging_init();
}

void mem_free_page(void *addr) {
    if ((unsigned int)addr < 0x100000) return;

    unsigned int page = (unsigned int)addr / 0x1000;
    paging_unmap(page);
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}