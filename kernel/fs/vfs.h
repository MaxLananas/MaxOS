#ifndef VFS_H
#define VFS_H

typedef struct {
    unsigned char type;
    union {
        void *ptr;
        struct {
            void *fat32_file;
        } fat32;
    } data;
} vfs_file;

void vfs_init(void);
vfs_file *vfs_open(const char *path);
unsigned int vfs_read(vfs_file *file, unsigned char *buffer, unsigned int size);
void vfs_close(vfs_file *file);
unsigned int vfs_seek(vfs_file *file, unsigned int position);

#endif