#include "vmm.h"
#include "screen.h"

void vmm_init(void) {
    screen_writeln("Virtual memory manager initialized", 0x0F);
}