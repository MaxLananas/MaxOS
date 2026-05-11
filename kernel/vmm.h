#ifndef VMM_H
#define VMM_H

void paging_init(void);
void heap_init(void *start, unsigned int size);
void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);

#endif