#ifndef MEM_H
#define MEM_H

void mem_init(unsigned int start, unsigned int end);
void mem_free_page(void *addr);
unsigned int mem_used_pages(void);

#endif