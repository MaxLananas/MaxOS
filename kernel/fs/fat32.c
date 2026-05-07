#include "fat32.h"
#include "../screen.h"
#include "../ata.h"

static fat32_bootsector bootsector;
static unsigned int fat_start;
static unsigned int data_start;
static unsigned int cluster_size;

void fat32_init(void) {
    unsigned char buffer[512];

    if(!ata_read(0, buffer, 1)) {
        screen_writeln("FAT32: Failed to read bootsector", 0x04);
        return;
    }

    fat32_bootsector *bs = (fat32_bootsector*)buffer;
    if(bs->boot_signature != 0x29) {
        screen_writeln("FAT32: Invalid boot signature", 0x04);
        return;
    }

    bootsector = *bs;
    fat_start = bootsector.reserved_sector_count;
    data_start = fat_start + (bootsector.table_count * bootsector.fat_size_32);
    cluster_size = bootsector.sectors_per_cluster * bootsector.bytes_per_sector;

    screen_writeln("FAT32: Filesystem initialized", 0x02);
}

fat32_file *fat32_open(const char *path) {
    fat32_file *file = (fat32_file*)1;
    file->inode = 0;
    file->offset = 0;
    file->size = 0;
    file->mode = 0;
    return file;
}

unsigned int fat32_read(fat32_file *file, unsigned char *buffer, unsigned int size) {
    return 0;
}

void fat32_close(fat32_file *file) {
}

unsigned int fat32_seek(fat32_file *file, unsigned int position) {
    return 0;
}