#include "fat32.h"
#include "../screen.h"
#include "../ata.h"

static fat32_bpb bpb;
static unsigned int fat_start;
static unsigned int data_start;
static unsigned int root_dir_cluster;

void fat32_init(void) {
    unsigned char buffer[FAT32_SECTOR_SIZE];

    if(!ata_read(0, buffer, 1)) {
        screen_writeln("FAT32: Failed to read boot sector", 0x04);
        return;
    }

    fat32_read_sector(0, buffer);
    fat32_read_sector(0, (unsigned char*)&bpb);

    if(bpb.bytes_per_sector != FAT32_SECTOR_SIZE) {
        screen_writeln("FAT32: Unsupported sector size", 0x04);
        return;
    }

    fat_start = bpb.reserved_sector_count;
    data_start = fat_start + (bpb.table_count * bpb.table_size_32);
    root_dir_cluster = bpb.root_cluster;

    screen_writeln("FAT32: Filesystem initialized", 0x02);
}

unsigned char fat32_read_sector(unsigned int lba, unsigned char *buffer) {
    return ata_read(lba, buffer, 1);
}

unsigned char fat32_write_sector(unsigned int lba, unsigned char *buffer) {
    return ata_write(lba, buffer, 1);
}

unsigned int fat32_get_next_cluster(unsigned int cluster) {
    unsigned int fat_offset = cluster * 4;
    unsigned int fat_sector = fat_start + (fat_offset / FAT32_SECTOR_SIZE);
    unsigned int entry_offset = fat_offset % FAT32_SECTOR_SIZE;
    unsigned char buffer[FAT32_SECTOR_SIZE];

    if(!fat32_read_sector(fat_sector, buffer)) {
        return 0x0FFFFFFF;
    }

    unsigned int next_cluster = *(unsigned int*)&buffer[entry_offset];
    return next_cluster & 0x0FFFFFFF;
}

void fat32_read_cluster(unsigned int cluster, unsigned char *buffer) {
    unsigned int sector = data_start + ((cluster - 2) * bpb.sectors_per_cluster);
    unsigned int sectors_to_read = bpb.sectors_per_cluster;

    for(unsigned int i = 0; i < sectors_to_read; i++) {
        if(!fat32_read_sector(sector + i, buffer + (i * FAT32_SECTOR_SIZE))) {
            screen_writeln("FAT32: Failed to read cluster", 0x04);
            return;
        }
    }
}

void fat32_write_cluster(unsigned int cluster, unsigned char *buffer) {
    unsigned int sector = data_start + ((cluster - 2) * bpb.sectors_per_cluster);
    unsigned int sectors_to_write = bpb.sectors_per_cluster;

    for(unsigned int i = 0; i < sectors_to_write; i++) {
        if(!fat32_write_sector(sector + i, buffer + (i * FAT32_SECTOR_SIZE))) {
            screen_writeln("FAT32: Failed to write cluster", 0x04);
            return;
        }
    }
}

fat32_file *fat32_open(const char *path) {
    fat32_file *file = (fat32_file*)0;
    unsigned char buffer[FAT32_SECTOR_SIZE];
    unsigned int current_cluster = root_dir_cluster;
    unsigned int next_cluster;
    unsigned int entry_index = 0;
    unsigned int sector_in_cluster = 0;
    unsigned int sector_offset = 0;

    while(1) {
        fat32_read_cluster(current_cluster, buffer);

        for(unsigned int i = 0; i < FAT32_SECTOR_SIZE / sizeof(fat32_dir_entry); i++) {
            fat32_dir_entry *entry = (fat32_dir_entry*)&buffer[i * sizeof(fat32_dir_entry)];

            if(entry->name[0] == 0x00) {
                return file;
            }

            if(entry->name[0] == 0xE5) {
                continue;
            }

            if((entry->attributes & 0x0F) == 0x0F) {
                continue;
            }

            char name[13];
            for(unsigned int j = 0; j < 8; j++) {
                if(entry->name[j] == ' ') break;
                name[j] = entry->name[j];
            }
            name[8] = '.';
            for(unsigned int j = 0; j < 3; j++) {
                if(entry->ext[j] == ' ') break;
                name[9 + j] = entry->ext[j];
            }
            name[12] = 0;

            if(strcmp(path, name) == 0) {
                file = (fat32_file*)1;
                file->cluster = entry->first_cluster_low | (entry->first_cluster_high << 16);
                file->position = 0;
                file->size = entry->file_size;
                file->mode = (entry->attributes & 0x10) ? 1 : 0;
                return file;
            }
        }

        next_cluster = fat32_get_next_cluster(current_cluster);
        if(next_cluster >= 0x0FFFFFF8) {
            return file;
        }
        current_cluster = next_cluster;
    }
}

unsigned int fat32_read(fat32_file *file, unsigned char *buffer, unsigned int size) {
    if(!file || file->mode != 0) return 0;

    unsigned int bytes_read = 0;
    unsigned int cluster = file->cluster;
    unsigned int position = file->position;
    unsigned int remaining = file->size - position;

    if(size > remaining) {
        size = remaining;
    }

    while(size > 0) {
        unsigned int cluster_offset = position % FAT32_CLUSTER_SIZE;
        unsigned int cluster_remaining = FAT32_CLUSTER_SIZE - cluster_offset;
        unsigned int to_read = (size < cluster_remaining) ? size : cluster_remaining;

        fat32_read_cluster(cluster, buffer + bytes_read);

        bytes_read += to_read;
        position += to_read;
        size -= to_read;

        if(size > 0) {
            cluster = fat32_get_next_cluster(cluster);
            if(cluster >= 0x0FFFFFF8) {
                break;
            }
        }
    }

    file->position = position;
    return bytes_read;
}

void fat32_close(fat32_file *file) {
    if(file) {
        file = (fat32_file*)0;
    }
}

unsigned int fat32_seek(fat32_file *file, unsigned int position) {
    if(!file || position > file->size) {
        return 0;
    }

    file->position = position;
    return position;
}