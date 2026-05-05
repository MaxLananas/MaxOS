#include "../drivers/screen.h"
#include "../kernel/io.h"
#include "../kernel/keyboard.h"

static char key_buffer[256];
static int buffer_index = 0;

void keyboard_init(void) {
    outb(0x21, inb(0x21) & 0xFD);
}

char keyboard_getchar(void) {
    while (1) {
        unsigned char status = inb(0x64);
        if (status & 0x01) {
            unsigned char keycode = inb(0x60);
            return keyboard_map(keycode);
        }
    }
}

static char keyboard_map(unsigned char keycode) {
    static char shift = 0;

    if (keycode == 0x2A || keycode == 0x36) {
        shift = 1;
        return 0;
    } else if (keycode == 0xAA || keycode == 0xB6) {
        shift = 0;
        return 0;
    }

    static const char scancode[] = {
        0, 27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
        '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
        0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
        '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' '
    };

    static const char scancode_shift[] = {
        0, 27, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '\b',
        '\t', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n',
        0, 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '~', 0,
        '|', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 0, '*', 0, ' '
    };

    if (keycode < 0x3B) {
        return shift ? scancode_shift[keycode] : scancode[keycode];
    }

    return 0;
}