#ifndef VMM_H
#define VMM_H

void heap_init(void *start, unsigned int size);
void heap_free(void *ptr);

#endif