#include "heap.h"
#include "screen.h"
#include "mem.h"

#define HEAP_START 0xC0000000
#define HEAP_SIZE 0x100000

typedef struct heap_block {
    unsigned int size;
    struct heap_block *next;
    int free;
} heap_block;

heap_block *heap_list = (heap_block*)HEAP_START;

void heap_init(void *start, unsigned int size) {
    screen_writeln("Initializing heap", 0x0A);

    heap_list->size = size - sizeof(heap_block);
    heap_list->next = 0;
    heap_list->free = 1;
}

void heap_free(void *ptr) {
    if (!ptr) return;

    heap_block *block = (heap_block*)((unsigned int)ptr - sizeof(heap_block));
    block->free = 1;

    heap_block *current = heap_list;
    while (current && current->next) {
        if (current->free && current->next->free) {
            current->size += sizeof(heap_block) + current->next->size;
            current->next = current->next->next;
        } else {
            current = current->next;
        }
    }
}