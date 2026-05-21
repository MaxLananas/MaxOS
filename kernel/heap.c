#include "heap.h"
#include "screen.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

static unsigned char heap[HEAP_SIZE];
static unsigned int heap_used = 0;

void heap_init(void *start, unsigned int size) {
    heap_used = 0;
    screen_writeln("Heap initialized", 0x0A);
}

void heap_free(void *ptr) {
    heap_used--;
}