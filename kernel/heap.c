#include "heap.h"
#include "screen.h"
#include "mem.h"

void heap_init(void *start, unsigned int size) {
    kmalloc_init(start, size);
    screen_writeln("Heap initialized", 0x0F);
}

void *heap_alloc(unsigned int size) {
    return kmalloc(size);
}

void heap_free(void *ptr) {
    kfree(ptr);
}