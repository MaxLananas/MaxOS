#ifndef KEYBOARD_H
#define KEYBOARD_H

#define KEY_NULL      0x00
#define KEY_BACKSPACE 0x08
#define KEY_TAB       0x09
#define KEY_ENTER     0x0A
#define KEY_ESCAPE    0x1B
#define KEY_UP        0x80
#define KEY_DOWN      0x81
#define KEY_LEFT      0x82
#define KEY_RIGHT     0x83
#define KEY_F1        0x84
#define KEY_F2        0x85
#define KEY_F3        0x86
#define KEY_F4        0x87
#define KEY_F5        0x88
#define KEY_F6        0x89
#define KEY_DELETE    0x8A
#define KEY_HOME      0x8B
#define KEY_END       0x8C

void kb_init(void);
char kb_getchar(void);
int  kb_haskey(void);

#endif