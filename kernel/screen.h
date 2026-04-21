#ifndef SCREEN_H
#define SCREEN_H

void screen_init();
void screen_write(const char* str,unsigned int len);
void screen_write_hex(unsigned int num);

#endif