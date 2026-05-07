#include "io.h"

#define MOUSE_PORT 0x60

void mouse_init(void) {
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        inb(MOUSE_PORT);
    }
}