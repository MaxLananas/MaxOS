#include "devfs.h"
#include "screen.h"

void devfs_init(void) {
    screen_writeln("DEVFS: Initialized", 0x02);
}