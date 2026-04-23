#include "ata.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

static unsigned short ata_primary_base = 0x1F0;
static unsigned short ata_secondary_base = 0x170;

static void ata_wait_busy(unsigned short base) {
    while (inb(base + ATA_STATUS) & ATA_SR_BSY);
}

static void ata_wait_drq(unsigned short base) {
    while (!(inb(base + ATA_STATUS) & ATA_SR_DRQ));
}

static unsigned char ata_identify(unsigned short base) {
    outb(base + ATA_DRIVE_SELECT, 0xA0);
    outb(base + ATA_SECTOR_COUNT, 0);
    outb(base + ATA_LBA_LOW, 0);
    outb(base + ATA_LBA_MID, 0);
    outb(base + ATA_LBA_HIGH, 0);
    outb(base + ATA_COMMAND, ATA_CMD_IDENTIFY);

    unsigned char status = inb(base + ATA_STATUS);
    if (status == 0) return 0;

    ata_wait_busy(base);
    ata_wait_drq(base);

    for (unsigned int i = 0; i < 256; i++) {
        inw(base + ATA_DATA);
    }

    return 1;
}

void ata_init() {
    if (ata_identify(ata_primary_base)) {
        screen_write("ATA Primary detected\n", 0x0F);
    }
    if (ata_identify(ata_secondary_base)) {
        screen_write("ATA Secondary detected\n", 0x0F);
    }
}

unsigned char ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    unsigned short base = (lba >> 24) & 0x0F ? ata_secondary_base : ata_primary_base;
    lba &= 0x0FFFFFFF;

    outb(base + ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(base + ATA_SECTOR_COUNT, sectors);
    outb(base + ATA_LBA_LOW, lba & 0xFF);
    outb(base + ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(base + ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(base + ATA_COMMAND, ATA_CMD_READ_PIO);

    for (unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy(base);
        ata_wait_drq(base);

        for (unsigned int j = 0; j < 256; j++) {
            unsigned short data = inw(base + ATA_DATA);
            buffer[j * 2] = data & 0xFF;
            buffer[j * 2 + 1] = (data >> 8) & 0xFF;
        }
        buffer += 512;
    }

    return 1;
}

unsigned char ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    unsigned short base = (lba >> 24) & 0x0F ? ata_secondary_base : ata_primary_base;
    lba &= 0x0FFFFFFF;

    outb(base + ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(base + ATA_SECTOR_COUNT, sectors);
    outb(base + ATA_LBA_LOW, lba & 0xFF);
    outb(base + ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(base + ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(base + ATA_COMMAND, ATA_CMD_WRITE_PIO);

    for (unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy(base);
        ata_wait_drq(base);

        for (unsigned int j = 0; j < 256; j++) {
            unsigned short data = (buffer[j * 2 + 1] << 8) | buffer[j * 2];
            outw(base + ATA_DATA, data);
        }
        buffer += 512;
    }

    return 1;
}