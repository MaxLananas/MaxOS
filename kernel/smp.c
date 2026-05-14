#include "smp.h"
#include "screen.h"

void smp_init(void) {
    screen_writeln("SMP initialized", 0x0F);
}