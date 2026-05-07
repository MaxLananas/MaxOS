#ifndef MEM_H
#define MEM_H

void heap_init(void *start, unsigned int size);
void heap_free(void *ptr);

#endif