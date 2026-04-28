#include "kernel/pmm.h"
#include "kernel/io.h"

#define PMM_BLOCKS_PER_BYTE 8
#define PMM_BLOCK_SIZE 4096
#define PMM_BLOCK_ALIGN PMM_BLOCK_SIZE

static unsigned int *bitmap;
static unsigned int bitmap_size;
static unsigned int max_blocks;

void pmm_init(unsigned int mem_size_kb) {
    max_blocks = mem_size_kb * 1024 / PMM_BLOCK_SIZE;
    bitmap_size = max_blocks / PMM_BLOCKS_PER_BYTE;
    bitmap = (unsigned int*)0x100000;
    for (unsigned int i = 0; i < bitmap_size; i++) {
        bitmap[i] = 0xFFFFFFFF;
    }
}

void pmm_set_block(unsigned int block) {
    bitmap[block / 32] &= ~(1 << (block % 32));
}

void pmm_unset_block(unsigned int block) {
    bitmap[block / 32] |= (1 << (block % 32));
}

unsigned int pmm_test_block(unsigned int block) {
    return bitmap[block / 32] & (1 << (block % 32));
}

void *pmm_alloc_block(void) {
    for (unsigned int i = 0; i < max_blocks; i++) {
        if (pmm_test_block(i)) {
            pmm_set_block(i);
            return (void*)(i * PMM_BLOCK_SIZE);
        }
    }
    return 0;
}

void pmm_free_block(void *addr) {
    unsigned int block = (unsigned int)addr / PMM_BLOCK_SIZE;
    pmm_unset_block(block);
}