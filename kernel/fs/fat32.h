#ifndef FAT32_H
#define FAT32_H

void fat32_init(void);
void *fat32_open(const char *path);
unsigned int fat32_read(void *file, unsigned char *buffer, unsigned int size);
void fat32_close(void *file);
unsigned int fat32_seek(void *file, unsigned int position);

#endif