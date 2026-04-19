#ifndef PCI_H
#define PCI_H

#define PCI_CONFIG_ADDRESS 0xCF8
#define PCI_CONFIG_DATA 0xCFC

#define PCI_CLASS_BRIDGE 0x06
#define PCI_CLASS_INPUT 0x01
#define PCI_CLASS_DISPLAY 0x03

#define PCI_SUBCLASS_KEYBOARD 0x01
#define PCI_SUBCLASS_VGA 0x00

typedef struct {
    unsigned short vendor_id;
    unsigned short device_id;
    unsigned char class_code;
    unsigned char subclass;
    unsigned char prog_if;
    unsigned char revision_id;
    unsigned char irq_line;
    unsigned int base_address[6];
} pci_device_t;

unsigned int pci_read_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset);
void pci_write_config(unsigned char bus, unsigned char slot, unsigned char func, unsigned char offset, unsigned int value);
void pci_scan_devices(void);
void pci_enable_bus_mastering(unsigned char bus, unsigned char slot, unsigned char func);
void pci_probe_keyboard(void);
void pci_probe_vga(void);

#endif