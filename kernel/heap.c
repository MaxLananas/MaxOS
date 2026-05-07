#include "heap.h"
#include "mem.h"
#include "screen.h"

typedef struct heap_block {
    unsigned int size;
    struct heap_block *next;
    int free;
} heap_block_t;

static heap_block_t *heap_start = 0;

void heap_init(void *start, unsigned int size) {
    heap_start = (heap_block_t*)start;
    heap_start->size = size - sizeof(heap_block_t);
    heap_start->next = 0;
    heap_start->free = 1;
}

void *heap_alloc(unsigned int size) {
    heap_block_t *current = heap_start;
    while (current) {
        if (current->free && current->size >= size) {
            if (current->size > size + sizeof(heap_block_t)) {
                heap_block_t *new_block = (heap_block_t*)((unsigned int)current + sizeof(heap_block_t) + size);
                new_block->size = current->size - size - sizeof(heap_block_t);
                new_block->next = current->next;
                new_block->free = 1;
                current->next = new_block;
                current->size = size;
            }
            current->free = 0;
            return (void*)((unsigned int)current + sizeof(heap_block_t));
        }
        current = current->next;
    }
    return 0;
}

void heap_free(void *ptr) {
    if (!ptr) return;
    heap_block_t *block = (heap_block_t*)((unsigned int)ptr - sizeof(heap_block_t));
    block->free = 1;

    heap_block_t *current = heap_start;
    while (current && current->next) {
        if (current->free && current->next->free) {
            current->size += sizeof(heap_block_t) + current->next->size;
            current->next = current->next->next;
        }
        current = current->next;
    }
}