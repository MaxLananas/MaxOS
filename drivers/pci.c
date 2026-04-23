#include "pci.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

#define PCI_CONFIG_ADDRESS 0xCF8
#define PCI_CONFIG_DATA 0xCFC

static unsigned int pci_read_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset) {
    unsigned int address = (1 << 31) | (bus << 16) | (slot << 11) | (func << 8) | (offset & 0xFC);
    outl(PCI_CONFIG_ADDRESS, address);
    return inl(PCI_CONFIG_DATA);
}

static void pci_write_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset, unsigned int value) {
    unsigned int address = (1 << 31) | (bus << 16) | (slot << 11) | (func << 8) | (offset & 0xFC);
    outl(PCI_CONFIG_ADDRESS, address);
    outl(PCI_CONFIG_DATA, value);
}

void pci_init() {
    screen_write("PCI Initialization\n", 0x0F);

    for (unsigned int bus = 0; bus < 256; bus++) {
        for (unsigned int slot = 0; slot < 32; slot++) {
            unsigned int vendor = pci_read_config(bus, slot, 0, 0) & 0xFFFF;
            if (vendor != 0xFFFF) {
                unsigned int class = (pci_read_config(bus, slot, 0, 0x0A) >> 8) & 0xFF;
                unsigned int subclass = pci_read_config(bus, slot, 0, 0x0A) & 0xFF;

                if (class == 0x01 && subclass == 0x01) {
                    screen_write("ATA Controller found\n", 0x0F);
                    ata_init();
                } else if (class == 0x0C && subclass == 0x03) {
                    screen_write("USB Controller found\n", 0x0F);
                    usb_init();
                }
            }
        }
    }
}