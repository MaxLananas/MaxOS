#ifndef VGA_H
#define VGA_H

#include "../kernel/io.h"

void vga_init(void);
void vga_putchar(char c, unsigned char fg, unsigned char bg);
void vga_clear(void);

#endif