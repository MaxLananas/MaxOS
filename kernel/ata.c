#include "ata.h"
#include "../kernel/io.h"
#include "../screen.h"

#define ATA_DATA 0x1F0
#define ATA_ERROR 0x1F1
#define ATA_SECTOR_COUNT 0x1F2
#define ATA_LBA_LOW 0x1F3
#define ATA_LBA_MID 0x1F4
#define ATA_LBA_HIGH 0x1F5
#define ATA_DRIVE_SELECT 0x1F6
#define ATA_COMMAND 0x1F7
#define ATA_STATUS 0x1F7

#define ATA_SR_BSY 0x80
#define ATA_SR_DRDY 0x40
#define ATA_SR_DF 0x20
#define ATA_SR_DSC 0x10
#define ATA_SR_DRQ 0x08
#define ATA_SR_CORR 0x04
#define ATA_SR_IDX 0x02
#define ATA_SR_ERR 0x01

static void ata_wait_busy(void) {
    while(inb(ATA_STATUS) & ATA_SR_BSY);
}

static void ata_wait_drq(void) {
    while(!(inb(ATA_STATUS) & ATA_SR_DRQ));
}

void ata_init(void) {
    screen_writeln("ATA: Initializing", 0x02);
}

unsigned char ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    ata_wait_busy();

    outb(ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_SECTOR_COUNT, sectors);
    outb(ATA_LBA_LOW, lba & 0xFF);
    outb(ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(ATA_COMMAND, 0x20);

    for(unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy();
        ata_wait_drq();

        for(unsigned int j = 0; j < 256; j++) {
            unsigned short data = inw(ATA_DATA);
            buffer[j * 2] = data & 0xFF;
            buffer[j * 2 + 1] = (data >> 8) & 0xFF;
        }
        buffer += 512;
    }

    return 1;
}

unsigned char ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors) {
    ata_wait_busy();

    outb(ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
    outb(ATA_SECTOR_COUNT, sectors);
    outb(ATA_LBA_LOW, lba & 0xFF);
    outb(ATA_LBA_MID, (lba >> 8) & 0xFF);
    outb(ATA_LBA_HIGH, (lba >> 16) & 0xFF);
    outb(ATA_COMMAND, 0x30);

    for(unsigned int i = 0; i < sectors; i++) {
        ata_wait_busy();
        ata_wait_drq();

        for(unsigned int j = 0; j < 256; j++) {
            unsigned short data = (buffer[j * 2 + 1] << 8) | buffer[j * 2];
            outw(ATA_DATA, data);
        }
        buffer += 512;
    }

    return 1;
}