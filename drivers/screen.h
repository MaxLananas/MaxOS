#ifndef SCREEN_H
#define SCREEN_H

#define C_BLACK 0x0

void v_init(void);
void v_put(unsigned int x, unsigned int y, char c, unsigned char fg, unsigned char bg);
void v_str(unsigned int x, unsigned int y, const char* s, unsigned char fg, unsigned char bg);
void v_fill(unsigned int x1, unsigned int y1, unsigned int x2, unsigned int y2, unsigned char fg, unsigned char bg);

#endif