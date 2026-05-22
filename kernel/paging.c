#include "paging.h"
#include "screen.h"
#include "mem.h"

#define PAGE_SIZE 4096
#define PAGE_PRESENT 1
#define PAGE_WRITE 2

extern void paging_load_directory(unsigned int *dir);

static unsigned int page_directory[1024] __attribute__((aligned(4096)));
static unsigned int page_table[1024] __attribute__((aligned(4096)));

void paging_init(void) {
    unsigned int i;
    for (i = 0; i < 1024; i++) {
        page_table[i] = (i * PAGE_SIZE) | PAGE_PRESENT | PAGE_WRITE;
    }

    page_directory[0] = (unsigned int)page_table | PAGE_PRESENT | PAGE_WRITE;
    for (i = 1; i < 1024; i++) {
        page_directory[i] = 0;
    }

    paging_load_directory(page_directory);
    screen_writeln("Paging initialized", 0x0A);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int table_idx = virt / (PAGE_SIZE * 1024);
    unsigned int entry_idx = (virt / PAGE_SIZE) % 1024;
    page_table[entry_idx] = phys | flags;
}