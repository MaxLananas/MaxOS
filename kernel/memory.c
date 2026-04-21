#include "memory.h"
#include "screen.h"

void mem_init(unsigned int start, unsigned int end) {
    screen_writeln("Memory initialized", 0x0A);
}

void mem_free_page(void *addr) {
}

unsigned int mem_used_pages(void) {
    return 0;
}

void heap_init(void *start, unsigned int size) {
}

void heap_free(void *ptr) {
}