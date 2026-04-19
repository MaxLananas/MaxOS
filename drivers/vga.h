#ifndef VGA_H
#define VGA_H

void outb(unsigned short port, unsigned char data);
unsigned char inb(unsigned short port);

void vga_init(void);
void vga_pixel(int x, int y, unsigned char c);
void vga_rect(int x, int y, int w, int h, unsigned char c);
void vga_fill(unsigned char c);
void vga_line(int x1, int y1, int x2, int y2, unsigned char c);

#endif