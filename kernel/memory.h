#ifndef MEMORY_H
#define MEMORY_H

void mem_init(unsigned int mem_size_kb);
void *mem_alloc_page(void);
void mem_free_page(void *addr);
unsigned int mem_used_pages(void);

#endif
