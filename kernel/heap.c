#include "heap.h"
#include "screen.h"

#define HEAP_SIZE 1024 * 1024

unsigned char heap[HEAP_SIZE];
unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    heap_pos = 0;
}

void heap_free(void *ptr) {
    // Simple free implementation
}

void *heap_alloc(unsigned int size) {
    void *ptr = &heap[heap_pos];
    heap_pos += size;
    if (heap_pos >= HEAP_SIZE) {
        return 0;
    }
    return ptr;
}