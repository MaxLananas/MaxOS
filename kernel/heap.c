#include "heap.h"

#define HEAP_START 0x100000
#define HEAP_SIZE 0x100000

unsigned char heap[HEAP_SIZE];
unsigned int heap_used = 0;

void heap_init(void *start, unsigned int size) {
    heap_used = 0;
}

void heap_free(void *ptr) {
    heap_used--;
}