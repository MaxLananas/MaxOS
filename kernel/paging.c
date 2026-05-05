#include "../kernel/paging.h"
#include "../drivers/screen.h"

void paging_init(void) {
    screen_writeln("Paging initialized", 0x0F);
}

void paging_map(unsigned int virt, unsigned int phys, unsigned int flags) {
}