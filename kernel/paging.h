#ifndef PAGING_H
#define PAGING_H

void paging_init(void);
void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);

#endif