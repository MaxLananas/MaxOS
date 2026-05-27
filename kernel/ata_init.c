#include "ata.h"
#include "screen.h"

void ata_init(void) {
    screen_writeln("ATA: Initialized", 0x02);
}