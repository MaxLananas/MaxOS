#include "mem.h"
#include "screen.h"
#include "paging.h"

void mem_init(unsigned int mem_size_kb) {
    pmm_init(mem_size_kb);
    screen_writeln("Memory manager initialized", 0x0F);
}

void *mem_alloc_page(void) {
    return pmm_alloc_page();
}

void mem_free_page(void *addr) {
    pmm_free_page(addr);
}

unsigned int mem_used_pages(void) {
    return pmm_used_pages();
}