#include "heap.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 0x100000

static unsigned char heap[HEAP_SIZE];
static unsigned int heap_ptr = 0;

void heap_init(void *start, unsigned int size) {
    heap_ptr = 0;
}

void *heap_alloc(unsigned int size) {
    if (heap_ptr + size > HEAP_SIZE) return 0;

    void *ptr = &heap[heap_ptr];
    heap_ptr += size;
    return ptr;
}

void heap_free(void *ptr) {
    // Simple bump allocator - no freeing
}