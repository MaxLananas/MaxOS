#include "heap.h"
#include "screen.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

unsigned char heap[HEAP_SIZE];
unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
}

void heap_free(void *ptr) {
}