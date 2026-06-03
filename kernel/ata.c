#include "ata.h"
#include "screen.h"

void ata_init(void) {
    screen_writeln("ATA initialized", 0x0F);
}