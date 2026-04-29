#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    screen_writeln("Keyboard initialized", 0x0A);
}

char keyboard_getchar(void) {
    if (buffer_pos > 0) {
        char c = keyboard_buffer[0];
        for (unsigned int i = 0; i < buffer_pos - 1; i++) {
            keyboard_buffer[i] = keyboard_buffer[i + 1];
        }
        buffer_pos--;
        return c;
    }
    return 0;
}