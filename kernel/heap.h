#ifndef HEAP_H
#define HEAP_H

void heap_init(void *start, unsigned int size);
void heap_free(void *ptr);
void *heap_alloc(unsigned int size);

#endif