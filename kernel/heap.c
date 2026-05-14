#include "heap.h"
#include "screen.h"

#define HEAP_START 0x100000
#define HEAP_SIZE 0x100000

unsigned char heap[HEAP_SIZE];
unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    heap_pos = 0;
}

void heap_free(void *ptr) {
    // Simple free implementation
}

void *heap_alloc(unsigned int size) {
    if (heap_pos + size > HEAP_SIZE) {
        return 0;
    }
    void *ptr = &heap[heap_pos];
    heap_pos += size;
    return ptr;
}