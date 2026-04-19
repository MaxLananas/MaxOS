#ifndef SCREEN_H
#define SCREEN_H

#define SCREEN_WIDTH_CHARS 80
#define SCREEN_HEIGHT_CHARS 25

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
#define C_LBROWN 0xE
#define C_WHITE 0xF

void v_init(void);
void v_put(unsigned int y, unsigned int x, char c, unsigned char bg, unsigned char fg);
void v_str(unsigned int y, unsigned int x, const char* s, unsigned char bg, unsigned char fg);
void v_fill(unsigned int y1, unsigned int x1, unsigned int y2, unsigned int x2, unsigned char bg, unsigned char fg);

#endif