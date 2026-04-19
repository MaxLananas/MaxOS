#ifndef SCREEN_H
#define SCREEN_H

#define C_BLACK 0x0
#define C_BLUE 0x1
#define C_GREEN 0x2
#define C_CYAN 0x3
#define C_RED 0x4
#define C_MAGENTA 0x5
#define C_BROWN 0x6
#define C_LGREY 0x7
#define C_DGREY 0x8
#define C_LBLUE 0x9
#define C_LGREEN 0xA
#define C_LCYAN 0xB
#define C_LRED 0xC
#define C_LMAGENTA 0xD
#define C_YELLOW 0xE
#define C_WHITE 0xF

void v_init(void);
void v_fill(unsigned int r1, unsigned int c1, unsigned int r2, unsigned int c2, unsigned char fg, unsigned char bg);
void v_str(unsigned int r, unsigned int c, const char* str, unsigned char fg, unsigned char bg);
void v_put(unsigned int r, unsigned int c, char ch, unsigned char fg, unsigned char bg);

#endif