#ifndef MEMORY_H
#define MEMORY_H

#define MAX_PAGES 1048576
#define PAGE_SIZE 4096

void mem_init(unsigned int start, unsigned int end);
void* kmalloc(unsigned int size);
void kfree(void* ptr);
void* kmalloc_ap(unsigned int size, unsigned int* phys);

#endif