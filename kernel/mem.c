#include "mem.h"

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
}

unsigned int mem_used_pages() {
    return used_pages;
}