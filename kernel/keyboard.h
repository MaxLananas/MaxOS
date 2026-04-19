#ifndef KEYBOARD_H
#define KEYBOARD_H

void kb_init(void);
unsigned char kb_haskey(void);
char kb_getchar(void);
void keyboard_handler(void);

#endif