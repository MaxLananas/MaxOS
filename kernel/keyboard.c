#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0
};

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~(1 << 1));
    screen_writeln("Keyboard initialized", 0x0F);
}

char keyboard_getchar(void) {
    unsigned char status;
    char keycode;

    status = inb(KEYBOARD_STATUS_PORT);
    if (status & 0x01) {
        keycode = inb(KEYBOARD_DATA_PORT);
        if (keycode < 128) {
            return keyboard_map[keycode];
        }
    }
    return 0;
}