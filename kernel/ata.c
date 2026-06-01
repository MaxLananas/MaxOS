#include "ata.h"
#include "../kernel/io.h"

void ata_wait_busy(void) {
    while(inb(0x1F7) & 0x80);
}

void ata_wait_drq(void) {
    while(!(inb(0x1F7) & 0x08));
}

int ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    outb(0x1F6, 0xE0 | ((lba >> 24) & 0x0F));
    outb(0x1F2, sectors);
    outb(0x1F3, lba & 0xFF);
    outb(0x1F4, (lba >> 8) & 0xFF);
    outb(0x1F5, (lba >> 16) & 0xFF);
    outb(0x1F7, 0x20);

    ata_wait_busy();
    ata_wait_drq();

    for(unsigned int i = 0; i < sectors; i++) {
        for(unsigned int j = 0; j < 256; j++) {
            unsigned short data = inw(0x1F0);
            buffer[j * 2] = data & 0xFF;
            buffer[j * 2 + 1] = (data >> 8) & 0xFF;
        }
        buffer += 512;
    }

    return 1;
}

int ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    outb(0x1F6, 0xE0 | ((lba >> 24) & 0x0F));
    outb(0x1F2, sectors);
    outb(0x1F3, lba & 0xFF);
    outb(0x1F4, (lba >> 8) & 0xFF);
    outb(0x1F5, (lba >> 16) & 0xFF);
    outb(0x1F7, 0x30);

    ata_wait_busy();
    ata_wait_drq();

    for(unsigned int i = 0; i < sectors; i++) {
        for(unsigned int j = 0; j < 256; j++) {
            unsigned short data = (buffer[j * 2 + 1] << 8) | buffer[j * 2];
            outw(0x1F0, data);
        }
        buffer += 512;
    }

    return 1;
}