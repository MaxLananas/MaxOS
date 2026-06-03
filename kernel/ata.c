#include "ata.h"
#include "io.h"
#include "screen.h"

#define ATA_DATA 0x1F0
#define ATA_ERROR 0x1F1
#define ATA_SECTOR_COUNT 0x1F2
#define ATA_LBA_LOW 0x1F3
#define ATA_LBA_MID 0x1F4
#define ATA_LBA_HIGH 0x1F5
#define ATA_DRIVE_SELECT 0x1F6
#define ATA_COMMAND 0x1F7
#define ATA_STATUS 0x1F7

void ata_wait_bsy(void) {
    while (inb(ATA_STATUS) & 0x80);
}

void ata_wait_drq(void) {
    while ((inb(ATA_STATUS) & 0x08) == 0);
}

void ata_identify(void) {
    outb(ATA_DRIVE_SELECT, 0xA0);
    outb(ATA_SECTOR_COUNT, 0);
    outb(ATA_LBA_LOW, 0);
    outb(ATA_LBA_MID, 0);
    outb(ATA_LBA_HIGH, 0);
    outb(ATA_COMMAND, 0xEC);
    ata_wait_bsy();
    ata_wait_drq();
}