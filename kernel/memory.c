#include "kernel/memory.h"
#include "kernel/pmm.h"
#include "kernel/vmm.h"
#include "kernel/heap.h"

void mem_init(unsigned int mem_size_kb) {
    pmm_init(mem_size_kb);
    vmm_init();
    heap_init((void*)0xC0000000, 1024 * 1024);
}