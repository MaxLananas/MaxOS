#ifndef ATA_H
#define ATA_H

void ata_init(void);
unsigned char ata_read(unsigned int lba, unsigned char *buffer, unsigned int sectors);
unsigned char ata_write(unsigned int lba, unsigned char *buffer, unsigned int sectors);

#endif