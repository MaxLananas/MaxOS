#include "pci.h"
#include "ata.h"
#include "usb.h"

void pci_init(void) {
    ata_init();
    usb_init();
}