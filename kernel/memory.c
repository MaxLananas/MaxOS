#include "memory.h"
#include "io.h"

#define BITMAP_SIZE (MAX_PAGES / 32)

static unsigned int bitmap[BITMAP_SIZE] = {0};

void mem_init(unsigned int start, unsigned int end) {
    unsigned int i;
    for (i = 0; i < BITMAP_SIZE; i++) {
        bitmap[i] = 0;
    }
}

void* kmalloc(unsigned int size) {
    unsigned int i, j, count;
    unsigned int addr = 0;

    for (i = 0; i < BITMAP_SIZE; i++) {
        if (bitmap[i] != 0xFFFFFFFF) {
            for (j = 0; j < 32; j++) {
                if (!(bitmap[i] & (1 << j))) {
                    count = 0;
                    while (count < size && (j + count) < 32) {
                        if (bitmap[i] & (1 << (j + count))) {
                            break;
                        }
                        count++;
                    }
                    if (count == size) {
                        addr = (i * 32 + j) * PAGE_SIZE;
                        for (count = 0; count < size; count++) {
                            bitmap[i] |= (1 << (j + count));
                        }
                        return (void*)addr;
                    }
                }
            }
        }
    }
    return 0;
}

void kfree(void* ptr) {
    if (ptr == 0) {
        return;
    }

    unsigned int addr = (unsigned int)ptr;
    unsigned int index = addr / PAGE_SIZE;

    if (index >= MAX_PAGES) {
        return;
    }

    unsigned int i = index / 32;
    unsigned int j = index % 32;

    bitmap[i] &= ~(1 << j);
}

void* kmalloc_ap(unsigned int size, unsigned int* phys) {
    void* addr = kmalloc(size);
    if (phys) {
        *phys = (unsigned int)addr;
    }
    return addr;
}