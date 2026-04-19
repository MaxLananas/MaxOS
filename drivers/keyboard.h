#ifndef KEYBOARD_H
#define KEYBOARD_H

#define KEY_NULL 0
#define KEY_F1 1
#define KEY_F2 2
#define KEY_F3 3
#define KEY_F4 4
#define KEY_TAB 5

void kb_init(void);
unsigned char kb_haskey(void);
char kb_getchar(void);

#endif