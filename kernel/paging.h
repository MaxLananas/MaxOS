#ifndef PAGING_H
#define PAGING_H

#define PAGE_PRESENT  0x1
#define PAGE_WRITE    0x2
#define PAGE_USER     0x4
#define PAGE_WRITETHROUGH 0x8
#define PAGE_CACHE_DISABLE 0x10
#define PAGE_ACCESSED 0x20
#define PAGE_DIRTY    0x40
#define PAGE_PAT      0x80
#define PAGE_GLOBAL   0x100

void paging_init(void);
void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);
void paging_unmap(unsigned int virt);
void paging_flush_tlb(void);

#endif