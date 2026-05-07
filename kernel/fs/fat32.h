#ifndef FAT32_H
#define FAT32_H

typedef struct {
    unsigned char jmp[3];
    unsigned char oem_name[8];
    unsigned short bytes_per_sector;
    unsigned char sectors_per_cluster;
    unsigned short reserved_sector_count;
    unsigned char table_count;
    unsigned short root_entry_count;
    unsigned short total_sectors_16;
    unsigned char media_type;
    unsigned short fat_size_16;
    unsigned short sectors_per_track;
    unsigned short head_side_count;
    unsigned int hidden_sector_count;
    unsigned int total_sectors_32;
    unsigned int fat_size_32;
    unsigned short ext_flags;
    unsigned short fs_version;
    unsigned int root_cluster;
    unsigned short fs_info;
    unsigned short backup_boot_sector;
    unsigned char reserved_0[12];
    unsigned char drive_number;
    unsigned char reserved_1;
    unsigned char boot_signature;
    unsigned int volume_id;
    unsigned char volume_label[11];
    unsigned char fs_type[8];
} __attribute__((packed)) fat32_bootsector;

typedef struct {
    unsigned int inode;
    unsigned int offset;
    unsigned int size;
    unsigned char mode;
} fat32_file;

void fat32_init(void);
fat32_file *fat32_open(const char *path);
unsigned int fat32_read(fat32_file *file, unsigned char *buffer, unsigned int size);
void fat32_close(fat32_file *file);
unsigned int fat32_seek(fat32_file *file, unsigned int position);