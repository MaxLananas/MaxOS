#include "mem.h"
#include "screen.h"

unsigned int mem_used = 0;

void mem_init(unsigned int mem_size_kb)
{
    screen_writeln("Memory initialized", 0x0F);
}

void mem_free_page(void *addr)
{
    mem_used--;
}

unsigned int mem_used_pages(void)
{
    return mem_used;
}