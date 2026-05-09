#include "heap.h"

static unsigned char heap[1024 * 1024]; // 1MB heap
static unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    // Simple heap initialization
    heap_pos = 0;
}

void heap_free(void *ptr) {
    // Simple heap free
}