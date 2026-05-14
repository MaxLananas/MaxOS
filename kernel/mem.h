#ifndef MEM_H
#define MEM_H

void mem_init(unsigned int mem_size_kb);
void mem_free_page(void *addr);
unsigned int mem_used_pages(void);
void paging_init(void);
void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);

#endif