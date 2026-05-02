#include "memory.h"
#include "screen.h"

#define MEMORY_SIZE 1024 * 1024

static unsigned char memory[MEMORY_SIZE];
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
    (void)addr;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}

void heap_init(void *start, unsigned int size) {
    (void)start;
    (void)size;
}

void heap_free(void *ptr) {
    (void)ptr;
}