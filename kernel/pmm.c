#include "pmm.h"
#include "io.h"
#include "memory.h"

pmm_manager_t pmm_manager;
unsigned int mem_start;

static void pmm_set_bit(unsigned int bit) {
    unsigned int idx = bit / 32;
    unsigned int offset = bit % 32;
    pmm_manager.bitmap[idx] |= (1 << offset);
}

static void pmm_clear_bit(unsigned int bit) {
    unsigned int idx = bit / 32;
    unsigned int offset = bit % 32;
    pmm_manager.bitmap[idx] &= ~(1 << offset);
}

static unsigned int pmm_test_bit(unsigned int bit) {
    unsigned int idx = bit / 32;
    unsigned int offset = bit % 32;
    return pmm_manager.bitmap[idx] & (1 << offset);
}

static unsigned int pmm_find_first_bit() {
    for (unsigned int i = 0; i < (pmm_manager.max_blocks / 32); i++) {
        if (pmm_manager.bitmap[i] != 0xFFFFFFFF) {
            for (unsigned int j = 0; j < 32; j++) {
                if (!(pmm_manager.bitmap[i] & (1 << j))) {
                    return i * 32 + j;
                }
            }
        }
    }
    return pmm_manager.max_blocks;
}

static void pmm_set_region(unsigned int base, unsigned int size) {
    unsigned int start_bit = (base - mem_start) / PMM_BLOCK_SIZE;
    unsigned int num_bits = size / PMM_BLOCK_SIZE;

    for (unsigned int i = 0; i < num_bits; i++) {
        pmm_set_bit(start_bit + i);
    }
}

static void pmm_init_bitmap() {
    for (unsigned int i = 0; i < (pmm_manager.max_blocks / 32); i++) {
        pmm_manager.bitmap[i] = 0xFFFFFFFF;
    }
}

void pmm_init(unsigned int start, unsigned int end) {
    mem_start = start;
    pmm_manager.max_blocks = (end - start) / PMM_BLOCK_SIZE;
    pmm_manager.used_blocks = 0;

    pmm_init_bitmap();
    pmm_set_region(start, end - start);
}

unsigned int pmm_alloc_block() {
    unsigned int bit = pmm_find_first_bit();
    if (bit == pmm_manager.max_blocks) {
        return 0;
    }

    pmm_set_bit(bit);
    pmm_manager.used_blocks++;
    return bit * PMM_BLOCK_SIZE + mem_start;
}

void pmm_free_block(unsigned int addr) {
    unsigned int bit = (addr - mem_start) / PMM_BLOCK_SIZE;
    if (bit >= pmm_manager.max_blocks) {
        return;
    }

    pmm_clear_bit(bit);
    pmm_manager.used_blocks--;
}

unsigned int pmm_alloc(unsigned int size) {
    if (size == 0) {
        return 0;
    }

    unsigned int num_blocks = (size + PMM_BLOCK_SIZE - 1) / PMM_BLOCK_SIZE;
    unsigned int order = 0;
    unsigned int block;

    while ((1 << order) < num_blocks) {
        order++;
    }

    for (; order < PMM_MAX_ORDER; order++) {
        block = pmm_find_first_bit();
        while (block + (1 << order) <= pmm_manager.max_blocks) {
            unsigned int i;
            for (i = 0; i < (1 << order); i++) {
                if (pmm_test_bit(block + i)) {
                    break;
                }
            }

            if (i == (1 << order)) {
                for (i = 0; i < (1 << order); i++) {
                    pmm_set_bit(block + i);
                }
                pmm_manager.used_blocks += (1 << order);
                return block * PMM_BLOCK_SIZE + mem_start;
            }

            block = pmm_find_first_bit();
        }
    }

    return 0;
}

void pmm_free(unsigned int addr, unsigned int size) {
    if (addr == 0 || size == 0) {
        return;
    }

    unsigned int num_blocks = (size + PMM_BLOCK_SIZE - 1) / PMM_BLOCK_SIZE;
    unsigned int block = (addr - mem_start) / PMM_BLOCK_SIZE;

    for (unsigned int i = 0; i < num_blocks; i++) {
        pmm_clear_bit(block + i);
    }

    pmm_manager.used_blocks -= num_blocks;
}

unsigned int pmm_get_phys_addr(unsigned int addr) {
    return addr - mem_start;
}