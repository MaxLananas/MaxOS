#include "mem.h"

#define MEM_START 0x100000
#define MEM_END 0x200000

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;

void mem_init(unsigned int size_kb) {
    mem_size_kb = size_kb;
    used_pages = 0;
}

unsigned int mem_used_pages() {
    return used_pages;
}