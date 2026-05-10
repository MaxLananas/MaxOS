#include "heap.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

typedef struct {
    unsigned int size;
    unsigned int used;
} heap_header;

heap_header *heap = (heap_header*)HEAP_START;

void heap_init(void *start, unsigned int size) {
    heap = (heap_header*)start;
    heap->size = size - sizeof(heap_header);
    heap->used = 0;
}

void *heap_alloc(unsigned int size) {
    if (size == 0) return 0;

    unsigned int block_size = size + sizeof(heap_header);
    unsigned int current = 0;

    while (current < heap->size) {
        heap_header *header = (heap_header*)((unsigned int)heap + sizeof(heap_header) + current);
        if (!header->used && header->size >= block_size) {
            header->used = 1;
            return (void*)((unsigned int)header + sizeof(heap_header));
        }
        current += header->size + sizeof(heap_header);
    }

    return 0;
}

void heap_free(void *ptr) {
    if (!ptr) return;

    heap_header *header = (heap_header*)((unsigned int)ptr - sizeof(heap_header));
    header->used = 0;
}