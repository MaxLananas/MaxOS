#include "heap.h"
#include "screen.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

static unsigned char heap[HEAP_SIZE];
static unsigned int heap_pos = 0;

void heap_init(void *start, unsigned int size) {
    (void)start;
    (void)size;
    heap_pos = 0;
    screen_writeln("Heap initialized", 0x0A);
}

void heap_free(void *ptr) {
    (void)ptr;
}

void *heap_alloc(unsigned int size) {
    void *ret = &heap[heap_pos];
    heap_pos += size;
    if (heap_pos > HEAP_SIZE) {
        return 0;
    }
    return ret;
}