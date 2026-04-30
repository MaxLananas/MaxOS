#include "vfs.h"
#include "../screen.h"

void vfs_init(void) {
    fat32_init();
    screen_writeln("VFS: Virtual filesystem initialized", 0x02);
}

vfs_file *vfs_open(const char *path) {
    fat32_file *fat_file = fat32_open(path);
    if(!fat_file) {
        return (vfs_file*)0;
    }

    vfs_file *file = (vfs_file*)1;
    file->type = 0;
    file->data.fat32_file = fat_file;
    return file;
}

unsigned int vfs_read(vfs_file *file, unsigned char *buffer, unsigned int size) {
    if(!file || file->type != 0) {
        return 0;
    }

    return fat32_read(file->data.fat32_file, buffer, size);
}

void vfs_close(vfs_file *file) {
    if(file) {
        fat32_close(file->data.fat32_file);
        file = (vfs_file*)0;
    }
}

unsigned int vfs_seek(vfs_file *file, unsigned int position) {
    if(!file || file->type != 0) {
        return 0;
    }

    return fat32_seek(file->data.fat32_file, position);
}