#include "keyboard.h"
#include "io.h"
#include "screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

void keyboard_init(void) {
    // Initialize keyboard
}

char keyboard_getchar(void) {
    return inb(KEYBOARD_DATA_PORT);
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    // Handle keyboard input
}