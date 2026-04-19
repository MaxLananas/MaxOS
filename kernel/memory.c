#include "memory.h"

unsigned int mem_start = 0;
unsigned int mem_end = 0;
unsigned int mem_ptr = 0;

void mem_init(unsigned int start, unsigned int end) {
    mem_start = start;
    mem_end = end;
    mem_ptr = start;
}

void* kmalloc(unsigned int size) {
    if (mem_ptr + size > mem_end) return 0;
    void* ptr = (void*)mem_ptr;
    mem_ptr += size;
    return ptr;
}

void kfree(void* ptr) {
}