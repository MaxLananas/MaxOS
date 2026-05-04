#ifndef KEYBOARD_H
#define KEYBOARD_H

void keyboard_init(void);
char keyboard_getchar(void);
void keyboard_handler(void);

extern const char keyboard_map[128];

#endif