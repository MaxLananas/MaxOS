#include "heap.h"
#include "screen.h"
#include "mem.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 1024 * 1024

typedef struct heap_block {
    unsigned int size;
    unsigned int used;
    struct heap_block *next;
} heap_block_t;

heap_block_t *heap_start = (heap_block_t*)HEAP_START;

void heap_init(void *start, unsigned int size) {
    heap_start = (heap_block_t*)start;
    heap_start->size = size - sizeof(heap_block_t);
    heap_start->used = 0;
    heap_start->next = 0;
}

void heap_free(void *ptr) {
    heap_block_t *block = (heap_block_t*)((unsigned int)ptr - sizeof(heap_block_t));
    block->used = 0;
}