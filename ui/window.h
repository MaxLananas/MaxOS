#ifndef WINDOW_H
#define WINDOW_H

typedef struct {
    unsigned int x;
    unsigned int y;
    unsigned int width;
    unsigned int height;
    const char* title;
    int is_active;
    int is_minimized;
} Window;

Window* window_create(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* title);
void window_draw(Window* window);
void window_activate(Window* window);
void window_minimize(Window* window);
void window_restore(Window* window);
void window_destroy(Window* window);

#endif