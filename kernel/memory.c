#include "memory.h"
#include "io.h"

unsigned char bitmap[MAX_PAGES / 8];
unsigned int mem_start = 0;
unsigned int mem_end = 0;
unsigned int mem_size = 0;

void mem_init(unsigned int start, unsigned int end) {
    mem_start = start;
    mem_end = end;
    mem_size = (end - start) / PAGE_SIZE;

    unsigned int i;
    for (i = 0; i < (MAX_PAGES / 8); i++) {
        bitmap[i] = 0;
    }

    for (i = 0; i < mem_size / 8; i++) {
        bitmap[i] = 0xFF;
    }
}

unsigned int find_free_page() {
    unsigned int i, j;
    for (i = 0; i < (mem_size / 8); i++) {
        if (bitmap[i] != 0xFF) {
            for (j = 0; j < 8; j++) {
                if (!(bitmap[i] & (1 << j))) {
                    return i * 8 + j;
                }
            }
        }
    }
    return 0;
}

void set_page_used(unsigned int page) {
    unsigned int idx = page / 8;
    unsigned int bit = page % 8;
    bitmap[idx] |= (1 << bit);
}

void set_page_free(unsigned int page) {
    unsigned int idx = page / 8;
    unsigned int bit = page % 8;
    bitmap[idx] &= ~(1 << bit);
}

void* kmalloc(unsigned int size) {
    unsigned int num_pages = (size + PAGE_SIZE - 1) / PAGE_SIZE;
    unsigned int start_page = find_free_page();

    if (start_page == 0 && num_pages > 1) {
        return 0;
    }

    unsigned int i;
    for (i = 0; i < num_pages; i++) {
        set_page_used(start_page + i);
    }

    return (void*)(mem_start + start_page * PAGE_SIZE);
}

void kfree(void* ptr) {
    unsigned int addr = (unsigned int)ptr;
    if (addr < mem_start || addr >= mem_end) {
        return;
    }

    unsigned int page = (addr - mem_start) / PAGE_SIZE;
    unsigned int num_pages = 1;

    set_page_free(page);
}