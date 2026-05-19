#include "heap.h"
#include "screen.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 0x100000

void *heap_start = (void *)HEAP_START;
unsigned int heap_size = HEAP_SIZE;
unsigned int heap_used = 0;

void heap_init(void *start, unsigned int size) {
    heap_start = start;
    heap_size = size;
    heap_used = 0;
}

void heap_free(void *ptr) {
    heap_used--;
}