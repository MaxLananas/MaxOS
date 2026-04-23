#include "vmm.h"
#include "io.h"
#include "memory.h"

static page_directory_t *current_directory = 0;
static page_directory_t kernel_directory = {0};
static page_directory_t *directories[1024] = {0};

void vmm_init(void) {
    unsigned int i = 0;
    for (i = 0; i < PAGE_DIR_ENTRIES; i++) {
        kernel_directory.tables[i] = 0;
        kernel_directory.tablesPhysical[i] = 0;
    }

    unsigned int phys = 0;
    for (i = 0; i < 1024; i++) {
        page_table_t *table = (page_table_t*)pmm_alloc_block();
        if (!table) return;

        for (unsigned int j = 0; j < PAGE_TABLE_ENTRIES; j++) {
            table->pages[j].present = 1;
            table->pages[j].rw = 1;
            table->pages[j].user = 0;
            table->pages[j].frame = (phys + j * PAGE_SIZE) >> 12;
        }

        kernel_directory.tables[i] = table;
        kernel_directory.tablesPhysical[i] = (unsigned int)table + 0xC0000000;
        phys += PAGE_SIZE * PAGE_TABLE_ENTRIES;
    }

    vmm_switch_page_directory(&kernel_directory);
    current_directory = &kernel_directory;
}

void vmm_map_page(unsigned int virt, unsigned int phys, unsigned int flags) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!current_directory->tables[pd_index]) {
        page_table_t *table = (page_table_t*)pmm_alloc_block();
        if (!table) return;

        for (unsigned int i = 0; i < PAGE_TABLE_ENTRIES; i++) {
            table->pages[i].present = 0;
            table->pages[i].rw = 0;
            table->pages[i].user = 0;
            table->pages[i].frame = 0;
        }

        current_directory->tables[pd_index] = table;
        current_directory->tablesPhysical[pd_index] = (unsigned int)table + 0xC0000000;
    }

    page_table_t *table = current_directory->tables[pd_index];
    table->pages[pt_index].present = 1;
    table->pages[pt_index].rw = (flags & 2) ? 1 : 0;
    table->pages[pt_index].user = (flags & 4) ? 1 : 0;
    table->pages[pt_index].frame = phys >> 12;
}

void vmm_unmap_page(unsigned int virt) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!current_directory->tables[pd_index]) return;

    page_table_t *table = current_directory->tables[pd_index];
    table->pages[pt_index].present = 0;
}

unsigned int vmm_get_phys(unsigned int virt) {
    unsigned int pd_index = virt >> 22;
    unsigned int pt_index = (virt >> 12) & 0x3FF;

    if (!current_directory->tables[pd_index]) return 0;

    page_table_t *table = current_directory->tables[pd_index];
    return (table->pages[pt_index].frame << 12) | (virt & 0xFFF);
}

void vmm_switch_page_directory(page_directory_t *dir) {
    unsigned int phys = (unsigned int)dir->tablesPhysical;
    __asm__ volatile("mov %0, %%cr3" :: "r"(phys));
    current_directory = dir;
}

page_directory_t *vmm_get_current_directory(void) {
    return current_directory;
}