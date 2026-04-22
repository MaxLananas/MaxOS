#include "paging.h"
#include "pmm.h"
#include "memory.h"
#include "io.h"

#define PAGE_SIZE 4096
#define PAGE_TABLE_ENTRIES 1024
#define PAGE_DIR_ENTRIES 1024

typedef struct {
    unsigned int entries[PAGE_TABLE_ENTRIES];
} page_table_t;

typedef struct {
    unsigned int entries[PAGE_DIR_ENTRIES];
} page_directory_t;

static page_directory_t *page_directory = (page_directory_t*)0xFFFFF000;
static page_table_t *page_tables = (page_table_t*)0xFFC00000;

void paging_flush_tlb(void) {
    unsigned int cr3;
    __asm__ volatile("mov %%cr3, %0" : "=r"(cr3));
    __asm__ volatile("mov %0, %%cr3" :: "r"(cr3));
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!(page_directory->entries[pd_index] & PAGE_PRESENT)) {
        unsigned int pt_phys = (unsigned int)pmm_alloc_block();
        if (!pt_phys) return;

        page_directory->entries[pd_index] = pt_phys | PAGE_PRESENT | PAGE_WRITE | PAGE_USER;
        page_tables[pd_index] = (page_table_t){0};
    }

    page_tables[pd_index].entries[pt_index] = phys | flags | PAGE_PRESENT;
    paging_flush_tlb();
}

void paging_unmap(unsigned int virt) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (page_directory->entries[pd_index] & PAGE_PRESENT) {
        page_tables[pd_index].entries[pt_index] = 0;
        paging_flush_tlb();
    }
}

void paging_init(void) {
    unsigned int i, j;

    for (i = 0; i < PAGE_DIR_ENTRIES; i++) {
        page_directory->entries[i] = 0;
    }

    for (i = 0; i < PAGE_DIR_ENTRIES; i++) {
        for (j = 0; j < PAGE_TABLE_ENTRIES; j++) {
            page_tables[i].entries[j] = 0;
        }
    }

    paging_map(0x0, 0x0, PAGE_WRITE);
    paging_map(0x100000, 0x100000, PAGE_WRITE);

    __asm__ volatile("mov %0, %%cr3" :: "r"(page_directory));
    unsigned int cr0;
    __asm__ volatile("mov %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    __asm__ volatile("mov %0, %%cr0" :: "r"(cr0));
}