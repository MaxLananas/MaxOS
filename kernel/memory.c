#include "memory.h"
#include "paging.h"

void mem_init(unsigned int mem_size_kb) {
    paging_init();
}