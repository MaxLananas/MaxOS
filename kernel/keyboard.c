#include "keyboard.h"
#include "io.h"
#include "idt.h"
#include "screen.h"
#include "terminal.h"

unsigned char keyboard_map[128] = {
    0,  27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`', 0,
    '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ',
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '-',
    0, 0, 0, 0, '+', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
};

void keyboard_init() {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
}

void keyboard_handler() {
    unsigned char scancode = inb(0x60);
    if (scancode < 128) {
        char c = keyboard_map[scancode];
        if (c) {
            terminal_process(&c);
        }
    }
}