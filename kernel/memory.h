#ifndef MEMORY_H
#define MEMORY_H

void mem_init(unsigned int start, unsigned int end);
void* kmalloc(unsigned int size);
void kfree(void* ptr);

#endif