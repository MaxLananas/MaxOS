#include "heap.h"
#include "screen.h"

void heap_init(void *start, unsigned int size) {
    screen_writeln("Heap initialized", 0x0A);
}

void heap_free(void *ptr) {
}