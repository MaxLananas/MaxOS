#ifndef KEYBOARD_H
#define KEYBOARD_H

#define KEY_NULL 0
#define KEY_F1 0x3B
#define KEY_F2 0x3C
#define KEY_F3 0x3D
#define KEY_F4 0x3E
#define KEY_TAB 0x0F

void kb_init(void);
int kb_haskey(void);
char kb_getchar(void);

#endif