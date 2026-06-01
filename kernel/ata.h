#ifndef ATA_H
#define ATA_H

int ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors);
int ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors);

#endif