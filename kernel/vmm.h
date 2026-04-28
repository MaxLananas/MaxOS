#ifndef VMM_H
#define VMM_H

void vmm_init(void);
void paging_init(void);
void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);

#endif