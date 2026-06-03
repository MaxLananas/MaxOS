#include "heap.h"
#include "screen.h"

#define HEAP_START 0x100000
#define HEAP_SIZE 0x100000

static unsigned char heap[HEAP_SIZE];
static unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    heap_pos = 0;
}

void heap_free(void *ptr) {
    (void)ptr;
}

unsigned int heap_used(void) {
    return heap_pos;
}