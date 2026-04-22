#ifndef PMM_H
#define PMM_H

#define PMM_BLOCK_SIZE 4096
#define PMM_MAX_ORDER 10

typedef struct {
    unsigned int *bitmap;
    unsigned int max_blocks;
    unsigned int used_blocks;
} pmm_manager_t;

void pmm_init(unsigned int start, unsigned int end);
unsigned int pmm_alloc_block(void);
void pmm_free_block(unsigned int addr);
unsigned int pmm_alloc(unsigned int size);
void pmm_free(unsigned int addr, unsigned int size);
unsigned int pmm_get_phys_addr(unsigned int addr);

#endif