#include "ata.h"
#include "screen.h"
#include "io.h"

void ata_init(void) {
    outb(0x1F6, 0xE0);
    outb(0x1F2, 0x00);
    outb(0x1F3, 0x00);
    outb(0x1F4, 0x00);
    outb(0x1F5, 0x00);
    outb(0x1F7, 0xEC);
    screen_writeln("ATA initialized", 0x0A);
}