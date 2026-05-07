#include "paging.h"
#include "io.h"

#define PAGE_SIZE 4096

extern void load_page_directory(unsigned int *page_directory);
extern void enable_paging(void);

static unsigned int *page_directory = (unsigned int*)0x9C000;
static unsigned int next_page = 0x100000;

void paging_init(void) {
    for (int i = 0; i < 1024; i++) {
        page_directory[i] = 0x00000002;
    }

    load_page_directory(page_directory);
    enable_paging();
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    unsigned int *page_table = (unsigned int*)(page_directory[pd_index] & 0xFFFFF000);
    if (!page_table) {
        page_table = (unsigned int*)next_page;
        next_page += 4096;
        page_directory[pd_index] = (unsigned int)page_table | flags | 0x01;
    }

    page_table[pt_index] = phys | flags | 0x01;
}