#include "memory.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define PAGE_TABLE_SIZE 1024
#define PAGE_DIR_SIZE 1024

static unsigned int *page_directory = (unsigned int*)0x100000;
static unsigned int *page_tables = (unsigned int*)0x101000;
static unsigned int next_page = 0x102000;

void mem_init(unsigned int mem_size_kb) {
    for (unsigned int i = 0; i < PAGE_DIR_SIZE; i++) {
        page_directory[i] = 0x00000002;
    }

    for (unsigned int i = 0; i < PAGE_TABLE_SIZE; i++) {
        page_tables[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = (unsigned int)page_tables | 3;
    next_page = 0x102000;
}

void *mem_alloc_page(void) {
    if (next_page >= 0x200000) return 0;
    void *addr = (void*)next_page;
    next_page += PAGE_SIZE;
    return addr;
}

void mem_free_page(void *addr) {
    // Simple implementation - no actual freeing in this basic version
}

unsigned int mem_used_pages(void) {
    return (next_page - 0x102000) / PAGE_SIZE;
}

void heap_init(void *start, unsigned int size) {
    // Simple heap initialization
}

void *heap_alloc(unsigned int size) {
    return 0; // Not implemented in this basic version
}

void heap_free(void *ptr) {
    // Not implemented
}