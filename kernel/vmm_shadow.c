#include "vmm_shadow.h"
#include "screen.h"

void vmm_shadow_init(void) {
    screen_writeln("VMM Shadow initialized", 0x0F);
}