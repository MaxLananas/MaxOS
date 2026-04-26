#ifndef PMM_H
#define PMM_H

void pmm_init(unsigned int mem_size_kb);
unsigned int pmm_get_free_pages(void);

#endif