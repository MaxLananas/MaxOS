#include "kernel/memory.h"

#define MAX_PAGES 32768
#define PAGE_SIZE 4096
#define KERNEL_END 0x100000

static unsigned int bitmap[MAX_PAGES / 32];
static unsigned int total_pages = 0;
static unsigned int used_pages  = 0;

static void bitmap_set(unsigned int page) {
    bitmap[page / 32] |= (1 << (page % 32));
}

static void bitmap_clear(unsigned int page) {
    bitmap[page / 32] &= ~(1 << (page % 32));
}

static int bitmap_test(unsigned int page) {
    return bitmap[page / 32] & (1 << (page % 32));
}

void mem_init(unsigned int mem_size_kb) {
    unsigned int i;
    total_pages = (mem_size_kb * 1024) / PAGE_SIZE;
    if (total_pages > MAX_PAGES) total_pages = MAX_PAGES;
    for (i = 0; i < MAX_PAGES / 32; i++) bitmap[i] = 0;
    for (i = 0; i < KERNEL_END / PAGE_SIZE; i++) bitmap_set(i);
    used_pages = KERNEL_END / PAGE_SIZE;
}

void *mem_alloc_page(void) {
    unsigned int i;
    for (i = 0; i < total_pages; i++) {
        if (!bitmap_test(i)) {
            bitmap_set(i);
            used_pages++;
            return (void *)(i * PAGE_SIZE);
        }
    }
    return 0;
}

void mem_free_page(void *addr) {
    unsigned int page = (unsigned int)addr / PAGE_SIZE;
    if (page < total_pages && bitmap_test(page)) {
        bitmap_clear(page);
        used_pages--;
    }
}

unsigned int mem_used_pages(void) {
    return used_pages;
}
