#include "window.h"
#include "screen.h"

void window_draw(window_t *window) {
    ui_draw_window(window->x, window->y, window->width, window->height, window->title);
}