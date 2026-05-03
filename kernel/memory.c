#include "memory.h"
#include "screen.h"

unsigned int mem_size_kb = 0;
unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    mem_size_kb = mem_size_kb;
    screen_writeln("Memory initialized", 0x0A);
}

unsigned int mem_used_pages(void) {
    return used_pages;
}