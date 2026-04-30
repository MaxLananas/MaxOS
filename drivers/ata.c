#include "ata.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

void ata_wait_busy(void) {
    for(unsigned int i = 0; i < 4; i++) {
        inb(ATA_STATUS);
    }
}

void ata_wait_drq(void) {
    while(!(inb(ATA_STATUS) & ATA_SR_DRQ));
}

unsigned char ata_identify(void) {
    outb(ATA_DRIVE_SELECT, 0xA0);
    outb(ATA_SECTOR_COUNT, 0);
    outb(ATA_LBA_LOW, 0);
    outb(ATA_LBA_MID, 0);
    outb(ATA_LBA_HIGH, 0);
    outb(ATA_COMMAND, ATA_CMD_IDENTIFY);
    ata_wait_busy();

    if(!(inb(ATA_STATUS) & ATA_SR_DRQ)) {
        return 0;
    }

    unsigned char buffer[512];
    for(unsigned int i = 0; i < 256; i++) {
        ((unsigned short*)buffer)[i] = inw(ATA_DATA);
    }

    return 1;
}

void ata_init(void) {
    if(!ata_identify()) {
        screen_writeln("ATA: No drive detected", 0x04);
        return;
    }

    screen_writeln("ATA: Drive initialized", 0x02);
}

unsigned char ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    outb(ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_SECTOR_COUNT, sectors);
    outb(ATA_LBA_LOW, lba & 0xFF);
    outb(ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(ATA_COMMAND, ATA_CMD_READ_PIO);

    for(unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy();
        ata_wait_drq();

        for(unsigned int j = 0; j < 256; j++) {
            ((unsigned short*)buffer)[j] = inw(ATA_DATA);
        }
        buffer += 512;
    }

    return 1;
}

unsigned char ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    outb(ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_SECTOR_COUNT, sectors);
    outb(ATA_LBA_LOW, lba & 0xFF);
    outb(ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(ATA_COMMAND, ATA_CMD_WRITE_PIO);

    for(unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy();
        ata_wait_drq();

        for(unsigned int j = 0; j < 256; j++) {
            outw(ATA_DATA, ((unsigned short*)buffer)[j]);
        }
        buffer += 512;
    }

    return 1;
}