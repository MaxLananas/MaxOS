#include "mem.h"
#include "screen.h"

static unsigned int mem_size_kb = 0;
static unsigned int used_pages = 0;

void mem_init(unsigned int size_kb)
{
    mem_size_kb = size_kb;
    screen_writeln("Memory initialized", 0x0F);
}

unsigned int mem_used_pages(void)
{
    return used_pages;
}