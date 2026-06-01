#include "vfs.h"
#include "screen.h"

void vfs_init(void) {
    screen_writeln("Virtual filesystem initialized", 0x0F);
}