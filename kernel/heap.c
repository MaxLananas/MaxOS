#include "kernel/io.h"

typedef struct block {
    unsigned int size;
    unsigned int free;
    struct block *next;
} block_t;

#define HEAP_START 0xC0000000
#define HEAP_SIZE 0x100000

static block_t *heap = (block_t*)HEAP_START;

void heap_init(void *start, unsigned int size) {
    heap = (block_t*)start;
    heap->size = size - sizeof(block_t);
    heap->free = 1;
    heap->next = 0;
}

void *heap_alloc(unsigned int size) {
    block_t *current = heap;
    block_t *prev = 0;

    while (current) {
        if (current->free && current->size >= size) {
            if (current->size > size + sizeof(block_t)) {
                block_t *new_block = (block_t*)((unsigned int)current + sizeof(block_t) + size);
                new_block->size = current->size - size - sizeof(block_t);
                new_block->free = 1;
                new_block->next = current->next;

                current->size = size;
                current->free = 0;
                current->next = new_block;
            } else {
                current->free = 0;
            }
            return (void*)((unsigned int)current + sizeof(block_t));
        }
        prev = current;
        current = current->next;
    }

    return 0;
}

void heap_free(void *ptr) {
    if (!ptr) return;

    block_t *block = (block_t*)((unsigned int)ptr - sizeof(block_t));
    block->free = 1;

    block_t *next = block->next;
    if (next && next->free) {
        block->size += sizeof(block_t) + next->size;
        block->next = next->next;
    }

    block_t *prev = heap;
    while (prev && prev->next != block) {
        prev = prev->next;
    }

    if (prev && prev->free) {
        prev->size += sizeof(block_t) + block->size;
        prev->next = block->next;
    }
}