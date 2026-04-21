#include "memory.h"

void mem_init(unsigned int start, unsigned int end) {
    (void)start;
    (void)end;
}

void mem_free_page(void *addr) {
    (void)addr;
}

unsigned int mem_used_pages(void) {
    return 0;
}

void heap_init(void *start, unsigned int size) {
    (void)start;
    (void)size;
}

void heap_free(void *ptr) {
    (void)ptr;
}