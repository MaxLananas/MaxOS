#include "heap.h"

#define HEAP_SIZE 1024 * 1024

static unsigned char heap[HEAP_SIZE];
static unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    // Simple heap initialization
    heap_pos = 0;
}

void heap_free(void *ptr) {
    // Simple free implementation - no actual freeing
}