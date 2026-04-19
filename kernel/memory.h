#ifndef MEMORY_H
#define MEMORY_H

#define MAX_PAGES 1024

void mem_init(unsigned int start, unsigned int end);
unsigned int mem_alloc(void);
void mem_free(unsigned int addr);
unsigned int mem_used(void);
unsigned int mem_total(void);

#endif