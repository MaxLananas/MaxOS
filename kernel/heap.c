#include "heap.h"
#include "screen.h"

#define HEAP_START 0x1000000
#define HEAP_SIZE 0x100000

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

void *heap_alloc(unsigned int size) {
    heap_block_t *current = heap_start;
    while (current) {
        if (!current->used && current->size >= size) {
            if (current->size > size + sizeof(heap_block_t)) {
                heap_block_t *new_block = (heap_block_t*)((unsigned int)current + sizeof(heap_block_t) + size);
                new_block->size = current->size - size - sizeof(heap_block_t);
                new_block->used = 0;
                new_block->next = current->next;
                current->size = size;
                current->next = new_block;
            }
            current->used = 1;
            return (void*)((unsigned int)current + sizeof(heap_block_t));
        }
        current = current->next;
    }
    return 0;
}