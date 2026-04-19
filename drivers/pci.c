#include "pci.h"
#include "../kernel/io.h"

unsigned int pci_read_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset) {
    unsigned int address = (1 << 31) | (bus << 16) | (slot << 11) | (func << 8) | (offset & 0xFC);
    outl(PCI_CONFIG_ADDRESS, address);
    return inl(PCI_CONFIG_DATA);
}

void pci_write_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset, unsigned int value) {
    unsigned int address = (1 << 31) | (bus << 16) | (slot << 11) | (func << 8) | (offset & 0xFC);
    outl(PCI_CONFIG_ADDRESS, address);
    outl(PCI_CONFIG_DATA, value);
}

void pci_scan_devices(void) {
    for (unsigned int bus = 0; bus < 256; bus++) {
        for (unsigned int slot = 0; slot < 32; slot++) {
            unsigned int vendor_device = pci_read_config(bus, slot, 0, 0);
            if (vendor_device == 0xFFFFFFFF || vendor_device == 0) {
                continue;
            }

            unsigned short vendor_id = vendor_device & 0xFFFF;
            unsigned short device_id = (vendor_device >> 16) & 0xFFFF;

            unsigned char class_code = (pci_read_config(bus, slot, 0, 0x0B) >> 16) & 0xFF;
            unsigned char subclass = (pci_read_config(bus, slot, 0, 0x0A) >> 8) & 0xFF;

            pci_device_t dev;
            dev.vendor_id = vendor_id;
            dev.device_id = device_id;
            dev.class_code = class_code;
            dev.subclass = subclass;
            dev.prog_if = (pci_read_config(bus, slot, 0, 0x09) >> 8) & 0xFF;
            dev.revision_id = pci_read_config(bus, slot, 0, 0x08) & 0xFF;
            dev.irq_line = pci_read_config(bus, slot, 0, 0x3C) & 0xFF;

            for (unsigned int i = 0; i < 6; i++) {
                unsigned int bar = pci_read_config(bus, slot, 0, 0x10 + i * 4);
                dev.base_address[i] = bar;
            }

            if (class_code == PCI_CLASS_INPUT && subclass == PCI_SUBCLASS_KEYBOARD) {
                pci_probe_keyboard();
            } else if (class_code == PCI_CLASS_DISPLAY && subclass == PCI_SUBCLASS_VGA) {
                pci_probe_vga();
            }
        }
    }
}

void pci_enable_bus_mastering(unsigned char bus, unsigned char slot, unsigned char func) {
    unsigned int command = pci_read_config(bus, slot, func, 0x04);
    command |= 0x04;
    pci_write_config(bus, slot, func, 0x04, command);
}

void pci_probe_keyboard(void) {
    pci_scan_devices();
}

void pci_probe_vga(void) {
    pci_scan_devices();
}