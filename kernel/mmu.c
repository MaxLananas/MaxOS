#include "mmu.h"
#include "screen.h"

void mmu_init(void) {
    screen_writeln("Memory management unit initialized", 0x0F);
}