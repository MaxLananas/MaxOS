#include "io.h"
#include "idt.h"
#include "../drivers/keyboard.h"
#include "../apps/terminal.h"

void main(unsigned int magic, unsigned int mbaddr) {
    keyboard_init();
    idt_install();

    tm_init();
    tm_print("Bare metal x86 OS\n");
    tm_print("> ");

    while (1) {
        asm volatile("hlt");
    }
}