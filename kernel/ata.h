#ifndef ATA_H
#define ATA_H

unsigned int ata_read(unsigned int lba, unsigned char *buffer);
unsigned int ata_write(unsigned int lba, const unsigned char *buffer);

#endif