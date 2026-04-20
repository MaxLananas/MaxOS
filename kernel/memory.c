#include "memory.h"
#include "paging.h"
#include "pmm.h"

void mem_init(unsigned int start, unsigned int end) {
    pmm_init(start, end);
}

void* kmalloc(unsigned int size) {
    unsigned int addr = pmm_alloc(size);
    return (void*)addr;
}

void kfree(void* ptr) {
    if (ptr == 0) {
        return;
    }

    unsigned int addr = (unsigned int)ptr;
    pmm_free(addr, 1);
}

void* kmalloc_ap(unsigned int size, unsigned int* phys) {
    void* addr = kmalloc(size);
    if (phys) {
        *phys = pmm_get_phys_addr((unsigned int)addr);
    }
    return addr;
}