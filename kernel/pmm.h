#ifndef PMM_H
#define PMM_H

void pmm_init(unsigned int mem_size_kb);
void pmm_set_block(unsigned int block);
void pmm_unset_block(unsigned int block);
unsigned int pmm_test_block(unsigned int block);
void *pmm_alloc_block(void);
void pmm_free_block(void *addr);

#endif