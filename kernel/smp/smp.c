#include "smp.h"
#include "smp_init.h"
#include "screen.h"

void smp_init(void) {
    smp_init();
    smp_start_aps();
    screen_writeln("SMP fully initialized", 0x0F);
}