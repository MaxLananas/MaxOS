#ifndef PAGING_H
#define PAGING_H

#include "memory.h"

#define PAGE_PRESENT  0x1
#define PAGE_WRITE    0x2
#define PAGE_USER     0x4
#define PAGE_WRITETHROUGH 0x8
#define PAGE_CACHE_DISABLE 0x10
#define PAGE_ACCESSED 0x20
#define PAGE_DIRTY    0x40
#define PAGE_PAT      0x80
#define PAGE_GLOBAL   0x100
#define PAGE_FRAME    0xFFFFF000

typedef struct page_table {
    unsigned int entries[1024];
} page_table_t;

typedef struct page_directory {
    unsigned int tables[1024];
    unsigned int phys_tables[1024];
} page_directory_t;

void paging_init();
void map_page(void* phys, void* virt, unsigned int flags);
void unmap_page(void* virt);
unsigned int virt_to_phys(void* virt);
void* phys_to_virt(unsigned int phys);
void switch_page_directory(page_directory_t* dir);
page_directory_t* clone_directory(page_directory_t* src);

#endif