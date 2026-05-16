#ifndef KEYBOARD_H
#define KEYBOARD_H

void keyboard_init(void);
void keyboard_handler(void);
char keyboard_getchar(void);

extern const unsigned char keyboard_map[128];

#endif