#ifndef WINDOW_H
#define WINDOW_H

typedef struct {
    unsigned short x;
    unsigned short y;
    unsigned short width;
    unsigned short height;
    const unsigned char *title;
} window_t;

void window_draw(window_t *window);

#endif