#include "fat32.h"
#include "../screen.h"
#include "../ata.h"
#include "../vfs.h"

static unsigned int fat_start;
static unsigned int data_start;
static unsigned int bytes_per_sector;
static unsigned int sectors_per_cluster;
static unsigned int reserved_sectors;
static unsigned int fat_count;
static unsigned int root_dir_sectors;

void fat32_init(void) {
    unsigned char buffer[512];

    if(!ata_read(0, buffer, 1)) {
        screen_writeln("FAT32: Failed to read bootsector", 0x04);
        return;
    }

    if(buffer[0] != 0xEB || buffer[2] != 0x90) {
        screen_writeln("FAT32: Invalid bootsector signature", 0x04);
        return;
    }

    bytes_per_sector = *(unsigned short*)(buffer + 11);
    sectors_per_cluster = buffer[13];
    reserved_sectors = *(unsigned short*)(buffer + 14);
    fat_count = buffer[16];
    fat_start = reserved_sectors;
    data_start = fat_start + fat_count * (*(unsigned int*)(buffer + 36));
    root_dir_sectors = ((*(unsigned short*)(buffer + 17)) * 32 + bytes_per_sector - 1) / bytes_per_sector;

    screen_writeln("FAT32: Filesystem initialized", 0x02);
}

void *fat32_open(const char *path) {
    return (void*)1;
}

unsigned int fat32_read(void *file, unsigned char *buffer, unsigned int size) {
    return 0;
}

void fat32_close(void *file) {
}

unsigned int fat32_seek(void *file, unsigned int position) {
    return 0;
}