#ifndef ATA_H
#define ATA_H

void ata_init(void);
void ata_read(unsigned int lba, unsigned char *buffer);

#endif