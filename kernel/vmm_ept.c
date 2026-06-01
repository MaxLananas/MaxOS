#include "vmm_ept.h"
#include "screen.h"

void vmm_ept_init(void) {
    screen_writeln("EPT memory manager initialized", 0x0F);
}