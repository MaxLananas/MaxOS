#include "mmu.h"
#include "screen.h"

void mmu_init(void) {
    screen_writeln("MMU initialized", 0x0F);
}