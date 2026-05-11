#include "heap.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

struct heap_header {
    unsigned int size;
    unsigned int used;
    struct heap_header *next;
};

struct heap_header *heap_first = (struct heap_header*)HEAP_START;

void heap_init(void *start, unsigned int size) {
    heap_first = (struct heap_header*)start;
    heap_first->size = size - sizeof(struct heap_header);
    heap_first->used = 0;
    heap_first->next = 0;
}

void heap_free(void *ptr) {
    struct heap_header *header = (struct heap_header*)((unsigned int)ptr - sizeof(struct heap_header));
    header->used = 0;
}