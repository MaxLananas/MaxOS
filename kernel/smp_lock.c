#include "smp_lock.h"
#include "screen.h"

void smp_lock_init(void) {
    screen_writeln("SMP lock initialized", 0x0F);
}