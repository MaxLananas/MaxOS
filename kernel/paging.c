#include "paging.h"
#include "screen.h"

#define PAGE_SIZE 4096
#define PAGE_DIRECTORY_ADDR 0x2000
#define PAGE_TABLE_ADDR 0x3000

void paging_init(void) {
    unsigned int *page_directory = (unsigned int *)PAGE_DIRECTORY_ADDR;
    unsigned int *page_table = (unsigned int *)PAGE_TABLE_ADDR;

    for (unsigned int i = 0; i < 1024; i++) {
        page_directory[i] = 0x00000002;
    }

    for (unsigned int i = 0; i < 1024; i++) {
        page_table[i] = (i * PAGE_SIZE) | 3;
    }

    page_directory[0] = (unsigned int)page_table | 3;
    asm volatile("movl %0, %%cr3" : : "r"(page_directory));
    unsigned int cr0;
    asm volatile("movl %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    asm volatile("movl %0, %%cr0" : : "r"(cr0));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int *page_directory = (unsigned int *)0x2000;
    unsigned int *page_table = (unsigned int *)(page_directory[virt / 4096000] & 0xFFFFF000);

    page_table[(virt / 4096) % 1024] = phys | flags;
    asm volatile("invlpg (%0)" : : "r"(virt) : "memory");
}