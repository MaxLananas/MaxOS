#ifndef PMM_H
#define PMM_H

#include "memory.h"

#define PMM_BLOCK_SIZE 4096
#define PMM_MAX_ORDER 11

typedef struct {
    unsigned int bitmap[1 << (PMM_MAX_ORDER - 5)];
    unsigned int max_blocks;
    unsigned int used_blocks;
} pmm_manager_t;

extern pmm_manager_t pmm_manager;
extern unsigned int mem_start;

void pmm_init(unsigned int start, unsigned int end);
unsigned int pmm_alloc(unsigned int size);
void pmm_free(unsigned int addr, unsigned int size);
unsigned int pmm_get_phys_addr(unsigned int addr);

#endif