#ifndef NOTEPAD_H
#define NOTEPAD_H

#include "../drivers/keyboard.h"

void np_init(void);
void np_draw(void);
void np_key(char k);

#endif