#ifndef KEYBOARD_H
#define KEYBOARD_H

extern const char keyboard_map[128];

void keyboard_init(void);
char keyboard_getchar(void);
void keyboard_handler(void);

#endif