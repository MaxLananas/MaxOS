#include "pmm.h"
#include "screen.h"

void pmm_init(unsigned int mem_size_kb) {
    screen_writeln("Physical memory manager initialized", 0x0F);
}

void *pmm_alloc_page(void) {
    return (void *)0x100000;
}

void pmm_free_page(void *addr) {
}

unsigned int pmm_used_pages(void) {
    return 0;
}