#include "memory.h"
#include "pmm.h"
#include "vmm.h"

#define MEMORY_SIZE 1024 * 1024 * 16

static unsigned char memory[MEMORY_SIZE];
static unsigned int used_pages = 0;

void mem_init(unsigned int mem_size_kb) {
    unsigned int mem_size = mem_size_kb * 1024;
    pmm_init((unsigned int)memory, (unsigned int)memory + mem_size);
    paging_init();
}

void mem_free_page(void *addr) {
    unsigned int phys = vmm_get_phys((unsigned int)addr);
    pmm_free_block(phys);
    used_pages--;
}

unsigned int mem_used_pages(void) {
    return used_pages;
}