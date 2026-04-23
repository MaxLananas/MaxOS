#include "paging.h"
#include "vmm.h"
#include "pmm.h"

void paging_init(void) {
    vmm_init();
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
    vmm_map_page(virt, phys, flags);
}