#ifndef VMM_H
#define VMM_H

#include "pmm.h"

#define PAGE_SIZE 4096
#define PAGE_TABLE_ENTRIES 1024
#define PAGE_DIR_ENTRIES 1024

typedef struct {
    unsigned int present    : 1;
    unsigned int rw         : 1;
    unsigned int user       : 1;
    unsigned int accessed   : 1;
    unsigned int dirty      : 1;
    unsigned int pat        : 1;
    unsigned int global     : 1;
    unsigned int unused     : 3;
    unsigned int frame      : 20;
} page_t;

typedef struct {
    page_t pages[PAGE_TABLE_ENTRIES];
} page_table_t;

typedef struct {
    page_table_t *tables[PAGE_DIR_ENTRIES];
    unsigned int tablesPhysical[PAGE_DIR_ENTRIES];
    unsigned int physicalAddr;
} page_directory_t;

void vmm_init(void);
void vmm_map_page(unsigned int virt, unsigned int phys, unsigned int flags);
void vmm_unmap_page(unsigned int virt);
unsigned int vmm_get_phys(unsigned int virt);
void vmm_switch_page_directory(page_directory_t *dir);
page_directory_t *vmm_get_current_directory(void);

#endif