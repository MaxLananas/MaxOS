#include "vmm_ept.h"
#include "screen.h"

void vmm_ept_init(void) {
    screen_writeln("VMM EPT initialized", 0x0F);
}