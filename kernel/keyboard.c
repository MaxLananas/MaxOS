#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    outb(0x64, 0xAE);
    outb(0x60, 0xF4);
}

char keyboard_getchar(void) {
    unsigned char scancode;
    while ((scancode = inb(0x64)) & 0x01) {
        unsigned char key = inb(0x60);
        if (key < 128) {
            return key;
        }
    }
    return 0;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        terminal_process((const char*)&scancode);
    }
}