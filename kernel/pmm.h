#ifndef PMM_H
#define PMM_H

void mem_init(unsigned int mem_size_kb);
void mem_free_page(void *addr);
unsigned int mem_used_pages(void);

#endif