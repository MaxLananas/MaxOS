#include "memory.h"

static unsigned int memory_bitmap[256];

static unsigned int mem_start_addr;
static unsigned int mem_end_addr;
static unsigned int total_managed_pages;

static void set_bit(unsigned int bit_index) {
    unsigned int array_index = bit_index / 32;
    unsigned int bit_offset = bit_index % 32;
    if (array_index < (sizeof(memory_bitmap) / sizeof(memory_bitmap[0]))) {
        memory_bitmap[array_index] |= (1 << bit_offset);
    }
}

static void clear_bit(unsigned int bit_index) {
    unsigned int array_index = bit_index / 32;
    unsigned int bit_offset = bit_index % 32;
    if (array_index < (sizeof(memory_bitmap) / sizeof(memory_bitmap[0]))) {
        memory_bitmap[array_index] &= ~(1 << bit_offset);
    }
}

static int test_bit(unsigned int bit_index) {
    unsigned int array_index = bit_index / 32;
    unsigned int bit_offset = bit_index % 32;
    if (array_index < (sizeof(memory_bitmap) / sizeof(memory_bitmap[0]))) {
        return (memory_bitmap[array_index] >> bit_offset) & 1;
    }
    return 0;
}

void mem_init(unsigned int start, unsigned int end) {
    unsigned int i;
    mem_start_addr = start;
    mem_end_addr = end;
    total_managed_pages = (mem_end_addr - mem_start_addr) / PAGE_SIZE;

    unsigned int bitmap_bytes_needed = (total_managed_pages + 7) / 8;
    unsigned int bitmap_uints_needed = (bitmap_bytes_needed + 3) / 4;

    for (i = 0; i < bitmap_uints_needed; i++) {
        memory_bitmap[i] = 0;
    }
    for (i = bitmap_uints_needed; i < (sizeof(memory_bitmap) / sizeof(memory_bitmap[0])); i++) {
        memory_bitmap[i] = 0;
    }
}

unsigned int mem_alloc(void) {
    unsigned int i;
    for (i = 0; i < total_managed_pages; i++) {
        if (!test_bit(i)) {
            set_bit(i);
            return mem_start_addr + (i * PAGE_SIZE);
        }
    }
    return 0;
}

void mem_free(unsigned int addr) {
    if (addr == 0) {
        return;
    }

    if (addr < mem_start_addr || addr >= mem_end_addr || (addr % PAGE_SIZE) != 0) {
        return;
    }

    unsigned int page_index = (addr - mem_start_addr) / PAGE_SIZE;

    if (page_index < total_managed_pages) {
        clear_bit(page_index);
    }
}

unsigned int mem_used_kb(void) {
    unsigned int used_pages = 0;
    unsigned int i;
    for (i = 0; i < total_managed_pages; i++) {
        if (test_bit(i)) {
            used_pages++;
        }
    }
    return used_pages * (PAGE_SIZE / 1024);
}

unsigned int mem_total_kb(void) {
    return total_managed_pages * (PAGE_SIZE / 1024);
}