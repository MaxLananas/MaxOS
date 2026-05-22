#include "mem.h"

#define PAGE_SIZE 4096
#define MEM_START 0x100000

static unsigned char mem_pool[0x100000];
static unsigned int mem_ptr = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_ptr = 0;
}

void *mem_alloc_page(void) {
    if (mem_ptr + PAGE_SIZE > sizeof(mem_pool)) return 0;

    void *ptr = &mem_pool[mem_ptr];
    mem_ptr += PAGE_SIZE;
    return ptr;
}

void mem_free_page(void *addr) {
    // Simple bump allocator - no freeing
}

unsigned int mem_used_pages(void) {
    return mem_ptr / PAGE_SIZE;
}