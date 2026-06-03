#ifndef MEM_H
#define MEM_H

void mem_init(unsigned int mem_size_kb);
unsigned int mem_used_pages(void);
void mem_free_page(void *addr);

#endif