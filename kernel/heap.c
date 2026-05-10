#include "heap.h"
#include "mem.h"

#define HEAP_START 0x200000
#define HEAP_SIZE 0x100000

unsigned char heap[HEAP_SIZE];
unsigned int heap_ptr = 0;

void heap_init(void *start, unsigned int size) {
    heap_ptr = 0;
}

void heap_free(void *ptr) {
    (void)ptr;
}