#include "memory.h"
#include "io.h"

#define PAGE_SIZE 4096

static unsigned int mem_bitmap[256];
static unsigned int mem_start_addr;
static unsigned int mem_end_addr;
static unsigned int mem_total_pages;
static unsigned int mem_used_pages;

void mem_init(unsigned int start, unsigned int end) {
    unsigned int i;
    mem_start_addr = start;
    mem_end_addr = end;
    mem_total_pages = (end - start) / PAGE_SIZE;
    mem_used_pages = 0;

    for (i = 0; i < 256; i++) {
        mem_bitmap[i] = 0;
    }

    unsigned int last_managed_page_idx = mem_total_pages;
    unsigned int bitmap_word_idx = last_managed_page_idx / 32;
    unsigned int bitmap_bit_idx = last_managed_page_idx % 32;

    if (bitmap_bit_idx != 0) {
        for (i = bitmap_bit_idx; i < 32; i++) {
            mem_bitmap[bitmap_word_idx] |= (1 << i);
        }
        bitmap_word_idx++;
    }

    for (i = bitmap_word_idx; i < 256; i++) {
        mem_bitmap[i] = 0xFFFFFFFF;
    }
}

unsigned int mem_alloc(void) {
    unsigned int i, j;
    for (i = 0; i < 256; i++) {
        if (mem_bitmap[i] != 0xFFFFFFFF) {
            for (j = 0; j < 32; j++) {
                if (!(mem_bitmap[i] & (1 << j))) {
                    unsigned int global_page_idx = i * 32 + j;
                    if (global_page_idx < mem_total_pages) {
                        mem_bitmap[i] |= (1 << j);
                        mem_used_pages++;
                        return mem_start_addr + global_page_idx * PAGE_SIZE;
                    }
                }
            }
        }
    }
    return 0;
}

void mem_free(unsigned int addr) {
    if (addr < mem_start_addr || addr >= mem_end_addr || (addr - mem_start_addr) % PAGE_SIZE != 0) {
        return;
    }

    unsigned int global_page_idx = (addr - mem_start_addr) / PAGE_SIZE;

    if (global_page_idx >= mem_total_pages) {
        return;
    }

    unsigned int i = global_page_idx / 32;
    unsigned int j = global_page_idx % 32;

    if (mem_bitmap[i] & (1 << j)) {
        mem_bitmap[i] &= ~(1 << j);
        mem_used_pages--;
    }
}

unsigned int mem_used(void) {
    return mem_used_pages * PAGE_SIZE;
}

unsigned int mem_total(void) {
    return mem_total_pages * PAGE_SIZE;
}