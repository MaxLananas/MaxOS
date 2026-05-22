#include "usb.h"
#include "pci.h"

void usb_init() {
    unsigned char bus, slot, func;
    if (pci_find_device(PCI_CLASS_USB, PCI_SUBCLASS_USB_XHCI, &bus, &slot, &func)) {
        unsigned int bar0 = pci_config_read_dword(bus, slot, func, 0x10);
        unsigned int base = bar0 & 0xFFFFFFF0;
        unsigned int caplength = inb(base);
        unsigned int hcsparams1 = inl(base + 0x04);
        unsigned int hccparams = inl(base + 0x10);

        outl(base + USB_XHCI_USBCMD, USB_XHCI_CMD_HCRST);
        while (inl(base + USB_XHCI_USBSTS) & USB_XHCI_STS_HCH);

        outl(base + USB_XHCI_USBCMD, USB_XHCI_CMD_RUN | USB_XHCI_CMD_INTE);
    }
}