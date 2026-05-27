#include "mem.h"
#include "screen.h"

static unsigned int mem_size_kb;
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb_param) {
    mem_size_kb = mem_size_kb_param;
    used_pages = 0;
}

void mem_free_page(void *addr) {
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}