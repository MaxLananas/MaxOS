#include "window.h"
#include "ui.h"
#include "../drivers/screen.h"

Window* window_create(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* title) {
    Window* window = (Window*)0x100000; // Simple allocation pour l'exemple
    window->x = x;
    window->y = y;
    window->width = width;
    window->height = height;
    window->title = title;
    window->is_active = 0;
    window->is_minimized = 0;
    return window;
}

void window_draw(Window* window) {
    if (window->is_minimized) return;
    ui_draw_window(window->x, window->y, window->width, window->height, window->title);
}

void window_activate(Window* window) {
    window->is_active = 1;
    window_draw(window);
}

void window_minimize(Window* window) {
    window->is_minimized = 1;
}

void window_restore(Window* window) {
    window->is_minimized = 0;
    window_draw(window);
}

void window_destroy(Window* window) {
    // Simple implementation - no actual memory free
    window->width = 0;
    window->height = 0;
}