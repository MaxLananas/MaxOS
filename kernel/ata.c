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

#define ATA_SR_BSY 0x80
#define ATA_SR_DRDY 0x40
#define ATA_SR_DF 0x20
#define ATA_SR_DSC 0x10
#define ATA_SR_DRQ 0x08
#define ATA_SR_CORR 0x04
#define ATA_SR_IDX 0x02
#define ATA_SR_ERR 0x01

#define ATA_CMD_READ_PIO 0x20
#define ATA_CMD_WRITE_PIO 0x30
#define ATA_CMD_IDENTIFY 0xEC

static void ata_wait_bsy(void) {
    while(inb(ATA_STATUS) & ATA_SR_BSY);
}

static void ata_wait_drdy(void) {
    while(!(inb(ATA_STATUS) & ATA_SR_DRDY));
}

static unsigned char ata_read_status(void) {
    return inb(ATA_STATUS);
}

static void ata_select_drive(unsigned char drive) {
    outb(ATA_DRIVE_SELECT, 0xE0 | (drive << 4));
    io_wait();
}

static void ata_send_command(unsigned char command) {
    outb(ATA_COMMAND, command);
    io_wait();
}

static void ata_set_lba(unsigned int lba) {
    outb(ATA_LBA_LOW, (unsigned char)(lba & 0xFF));
    outb(ATA_LBA_MID, (unsigned char)((lba >> 8) & 0xFF));
    outb(ATA_LBA_HIGH, (unsigned char)((lba >> 16) & 0xFF));
    outb(ATA_DRIVE_SELECT, 0xE0 | ((lba >> 24) & 0x0F));
}

void ata_init(void) {
    ata_select_drive(0);
    ata_wait_drdy();
    screen_writeln("ATA: Primary IDE controller initialized", 0x02);
}

unsigned int ata_read(block_device_t *dev, unsigned int lba, unsigned char *buffer) {
    unsigned int count = 1;
    unsigned short *buf = (unsigned short*)buffer;

    ata_select_drive(0);
    ata_wait_bsy();
    ata_wait_drdy();

    outb(ATA_SECTOR_COUNT, count);
    ata_set_lba(lba);

    ata_send_command(ATA_CMD_READ_PIO);

    for(unsigned int i = 0; i < count; i++) {
        ata_wait_bsy();
        ata_wait_drdy();

        for(unsigned int j = 0; j < 256; j++) {
            buf[j] = inw(ATA_DATA);
        }
    }

    return count * BLOCK_SIZE;
}

unsigned int ata_write(block_device_t *dev, unsigned int lba, const unsigned char *buffer) {
    unsigned int count = 1;
    unsigned short *buf = (unsigned short*)buffer;

    ata_select_drive(0);
    ata_wait_bsy();
    ata_wait_drdy();

    outb(ATA_SECTOR_COUNT, count);
    ata_set_lba(lba);

    ata_send_command(ATA_CMD_WRITE_PIO);

    for(unsigned int i = 0; i < count; i++) {
        ata_wait_bsy();
        ata_wait_drdy();

        for(unsigned int j = 0; j < 256; j++) {
            outw(ATA_DATA, buf[j]);
        }
    }

    return count * BLOCK_SIZE;
}