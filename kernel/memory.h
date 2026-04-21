#ifndef MEMORY_H
#define MEMORY_H

void mem_init(unsigned int start, unsigned int end);
void mem_free_page(void *addr);
unsigned int mem_used_pages(void);
void heap_init(void *start, unsigned int size);
void heap_free(void *ptr);

#endif