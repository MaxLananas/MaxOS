#include "vmm.h"
#include "screen.h"

void vmm_init(void) {
    screen_writeln("VMM initialized", 0x0A);
}