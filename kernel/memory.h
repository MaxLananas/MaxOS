#ifndef MEMORY_H
#define MEMORY_H

#define PAGE_SIZE 0x1000

void mem_init(unsigned int start, unsigned int end);
unsigned int mem_alloc(void);
void mem_free(unsigned int addr);
unsigned int mem_used_kb(void);
unsigned int mem_total_kb(void);

#endif