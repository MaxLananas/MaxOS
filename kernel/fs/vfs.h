#ifndef VFS_H
#define VFS_H

#include "fat32.h"

typedef struct {
    unsigned char type;
    union {
        fat32_file *fat32_file;
    } data;
} vfs_file;

void vfs_init(void);
vfs_file *vfs_open(const char *path);
unsigned int vfs_read(vfs_file *file, unsigned char *buffer, unsigned int size);
void vfs_close(vfs_file *file);
unsigned int vfs_seek(vfs_file *file, unsigned int position);

#endif