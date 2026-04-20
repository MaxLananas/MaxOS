#include "paging.h"
#include "memory.h"
#include "io.h"

static page_directory_t* kernel_directory = 0;
static page_directory_t* current_directory = 0;

void paging_init() {
    kernel_directory = (page_directory_t*)kmalloc(sizeof(page_directory_t));
    current_directory = kernel_directory;

    unsigned int i;
    for (i = 0; i < 1024; i++) {
        kernel_directory->tables[i] = 0;
        kernel_directory->phys_tables[i] = 0;
    }

    for (i = 0; i < 1024; i++) {
        page_table_t* table = (page_table_t*)kmalloc_ap(sizeof(page_table_t), &kernel_directory->phys_tables[i]);
        kernel_directory->tables[i] = (unsigned int)table | PAGE_PRESENT | PAGE_WRITE;

        unsigned int j;
        for (j = 0; j < 1024; j++) {
            unsigned int addr = i * 0x400000 + j * 0x1000;
            table->entries[j] = addr | PAGE_PRESENT | PAGE_WRITE;
        }
    }

    switch_page_directory(kernel_directory);
}

void map_page(void* phys, void* virt, unsigned int flags) {
    unsigned int pd_index = (unsigned int)virt >> 22;
    unsigned int pt_index = (unsigned int)virt >> 12 & 0x3FF;

    page_table_t* table = (page_table_t*)(current_directory->tables[pd_index] & PAGE_FRAME);

    if (!table) {
        unsigned int phys_table;
        table = (page_table_t*)kmalloc_ap(sizeof(page_table_t), &phys_table);
        current_directory->tables[pd_index] = (unsigned int)table | PAGE_PRESENT | PAGE_WRITE;
        current_directory->phys_tables[pd_index] = phys_table | PAGE_PRESENT | PAGE_WRITE;
    }

    table->entries[pt_index] = ((unsigned int)phys) | flags;
}

void unmap_page(void* virt) {
    unsigned int pd_index = (unsigned int)virt >> 22;
    unsigned int pt_index = (unsigned int)virt >> 12 & 0x3FF;

    page_table_t* table = (page_table_t*)(current_directory->tables[pd_index] & PAGE_FRAME);
    if (table) {
        table->entries[pt_index] = 0;
    }
}

unsigned int virt_to_phys(void* virt) {
    unsigned int pd_index = (unsigned int)virt >> 22;
    unsigned int pt_index = (unsigned int)virt >> 12 & 0x3FF;

    page_table_t* table = (page_table_t*)(current_directory->tables[pd_index] & PAGE_FRAME);
    if (!table) return 0;

    return table->entries[pt_index] & PAGE_FRAME;
}

void* phys_to_virt(unsigned int phys) {
    return (void*)(phys + 0xC0000000);
}

void switch_page_directory(page_directory_t* dir) {
    current_directory = dir;
    asm volatile("mov %0, %%cr3" : : "r"(dir->phys_tables));
    unsigned int cr0;
    asm volatile("mov %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000;
    asm volatile("mov %0, %%cr0" : : "r"(cr0));
}

page_directory_t* clone_directory(page_directory_t* src) {
    page_directory_t* dir = (page_directory_t*)kmalloc_ap(sizeof(page_directory_t), 0);
    unsigned int phys_dir;
    if (!dir) return 0;

    unsigned int i;
    for (i = 0; i < 1024; i++) {
        if (!src->tables[i]) {
            dir->tables[i] = 0;
            dir->phys_tables[i] = 0;
        } else {
            unsigned int phys;
            page_table_t* table = (page_table_t*)kmalloc_ap(sizeof(page_table_t), &phys);
            if (!table) return 0;

            dir->tables[i] = (unsigned int)table | PAGE_PRESENT | PAGE_WRITE;
            dir->phys_tables[i] = phys | PAGE_PRESENT | PAGE_WRITE;

            page_table_t* src_table = (page_table_t*)(src->tables[i] & PAGE_FRAME);
            unsigned int j;
            for (j = 0; j < 1024; j++) {
                if (src_table->entries[j] & PAGE_PRESENT) {
                    table->entries[j] = src_table->entries[j];
                } else {
                    table->entries[j] = 0;
                }
            }
        }
    }
    return dir;
}