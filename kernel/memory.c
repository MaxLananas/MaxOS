#include "memory.h"
#include "io.h"

static unsigned int bitmap[MAX_PAGES/32];
static unsigned int mem_start;
static unsigned int mem_end;
static unsigned int total_pages;

void mem_init(unsigned int start, unsigned int end) {
    unsigned int i;
    mem_start = start;
    mem_end = end;
    total_pages = (end - start) / PAGE_SIZE;

    for (i = 0; i < MAX_PAGES/32; i++) {
        bitmap[i] = 0;
    }

    unsigned int last_page = total_pages;
    unsigned int word_idx = last_page / 32;
    unsigned int bit_idx = last_page % 32;

    if (bit_idx != 0) {
        for (i = bit_idx; i < 32; i++) {
            bitmap[word_idx] |= (1 << i);
        }
        word_idx++;
    }

    for (i = word_idx; i < MAX_PAGES/32; i++) {
        bitmap[i] = 0xFFFFFFFF;
    }
}

unsigned int mem_alloc(void) {
    unsigned int i, j;
    for (i = 0; i < MAX_PAGES/32; i++) {
        if (bitmap[i] != 0xFFFFFFFF) {
            for (j = 0; j < 32; j++) {
                if (!(bitmap[i] & (1 << j))) {
                    unsigned int page = i * 32 + j;
                    if (page < total_pages) {
                        bitmap[i] |= (1 << j);
                        return mem_start + page * PAGE_SIZE;
                    }
                }
            }
        }
    }
    return 0;
}

void mem_free(unsigned int addr) {
    if (addr < mem_start || addr >= mem_end || (addr - mem_start) % PAGE_SIZE != 0) {
        return;
    }

    unsigned int page = (addr - mem_start) / PAGE_SIZE;
    unsigned int i = page / 32;
    unsigned int j = page % 32;

    if (bitmap[i] & (1 << j)) {
        bitmap[i] &= ~(1 << j);
    }
}

unsigned int mem_used(void) {
    unsigned int count = 0;
    unsigned int i, j;
    for (i = 0; i < MAX_PAGES/32; i++) {
        for (j = 0; j < 32; j++) {
            if (bitmap[i] & (1 << j)) {
                count++;
            }
        }
    }
    return count * PAGE_SIZE;
}

unsigned int mem_total(void) {
    return total_pages * PAGE_SIZE;
}