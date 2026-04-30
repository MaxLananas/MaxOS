#ifndef FAT32_H
#define FAT32_H

#include "../ata.h"

#define FAT32_SECTOR_SIZE 512
#define FAT32_CLUSTER_SIZE 4096
#define FAT32_MAX_PATH 256

typedef struct {
    unsigned char bootjmp[3];
    unsigned char oem_name[8];
    unsigned short bytes_per_sector;
    unsigned char sectors_per_cluster;
    unsigned short reserved_sector_count;
    unsigned char table_count;
    unsigned short root_entry_count;
    unsigned short total_sectors_16;
    unsigned char media_type;
    unsigned short table_size_16;
    unsigned short sectors_per_track;
    unsigned short head_side_count;
    unsigned int hidden_sector_count;
    unsigned int total_sectors_32;
    unsigned int table_size_32;
    unsigned short extended_flags;
    unsigned short fat_version;
    unsigned int root_cluster;
    unsigned short fat_info;
    unsigned short backup_boot_sector;
    unsigned char reserved_0[12];
    unsigned char drive_number;
    unsigned char reserved_1;
    unsigned char boot_signature;
    unsigned int volume_id;
    unsigned char volume_label[11];
    unsigned char fat_type_label[8];
} __attribute__((packed)) fat32_bpb;

typedef struct {
    unsigned char name[8];
    unsigned char ext[3];
    unsigned char attributes;
    unsigned char reserved;
    unsigned char creation_time_tenth;
    unsigned short creation_time;
    unsigned short creation_date;
    unsigned short last_access_date;
    unsigned short first_cluster_high;
    unsigned short last_write_time;
    unsigned short last_write_date;
    unsigned short first_cluster_low;
    unsigned int file_size;
} __attribute__((packed)) fat32_dir_entry;

typedef struct {
    unsigned int cluster;
    unsigned int position;
    unsigned int size;
    unsigned char mode;
} fat32_file;

void fat32_init(void);
unsigned char fat32_read_sector(unsigned int lba, unsigned char *buffer);
unsigned char fat32_write_sector(unsigned int lba, unsigned char *buffer);
unsigned int fat32_get_next_cluster(unsigned int cluster);
void fat32_read_cluster(unsigned int cluster, unsigned char *buffer);
void fat32_write_cluster(unsigned int cluster, unsigned char *buffer);
fat32_file *fat32_open(const char *path);
unsigned int fat32_read(fat32_file *file, unsigned char *buffer, unsigned int size);
void fat32_close(fat32_file *file);
unsigned int fat32_seek(fat32_file *file, unsigned int position);

#endif