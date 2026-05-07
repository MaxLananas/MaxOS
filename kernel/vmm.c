#include "vmm.h"
#include "screen.h"

extern void paging_init(void);
extern void paging_map(unsigned int virt, unsigned int phys, unsigned int flags);

void vmm_init(void) {
    paging_init();
}