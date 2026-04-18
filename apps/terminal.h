#ifndef TERMINAL_H
#define TERMINAL_H

#include "../drivers/keyboard.h"

void tm_init(void);
void tm_draw(void);
void tm_key(char k);

#endif