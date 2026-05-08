#include "kernel/heap.h"
#include "kernel/mem.h"

typedef struct heap_block {
    unsigned int size;
    unsigned int used;
    struct heap_block *next;
} heap_block_t;

static heap_block_t *heap_start = 0;
static heap_block_t *heap_end = 0;

void heap_init(void *start, unsigned int size) {
    heap_start = (heap_block_t*)start;
    heap_start->size = size - sizeof(heap_block_t);
    heap_start->used = 0;
    heap_start->next = 0;
    heap_end = heap_start;
}

void heap_free(void *ptr) {
    if (!ptr) return;

    heap_block_t *block = (heap_block_t*)((unsigned char*)ptr - sizeof(heap_block_t));
    block->used = 0;

    // Merge with next block if free
    if (block->next && !block->next->used) {
        block->size += sizeof(heap_block_t) + block->next->size;
        block->next = block->next->next;
        if (block->next == 0) heap_end = block;
    }

    // Merge with previous block if free
    heap_block_t *prev = heap_start;
    while (prev && prev->next != block) prev = prev->next;
    if (prev && !prev->used) {
        prev->size += sizeof(heap_block_t) + block->size;
        prev->next = block->next;
        if (block->next == 0) heap_end = prev;
    }
}