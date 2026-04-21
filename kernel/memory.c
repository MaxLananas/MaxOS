static unsigned int *frames;
static unsigned int nframes;

void mem_init(unsigned int mem_size_kb) {
    unsigned int mem_size_bytes = mem_size_kb * 1024;
    nframes = mem_size_bytes / 4096;
    frames = (unsigned int*)0x100000;
    for (unsigned int i = 0; i < nframes; i++) {
        frames[i] = 0;
    }
}

void mem_free_page(void *addr) {
    unsigned int frame = (unsigned int)addr / 4096;
    frames[frame] = 0;
}

unsigned int mem_used_pages(void) {
    unsigned int count = 0;
    for (unsigned int i = 0; i < nframes; i++) {
        if (frames[i]) {
            count++;
        }
    }
    return count;
}