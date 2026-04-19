#ifndef WIDGET_H
#define WIDGET_H

typedef struct {
    unsigned int x;
    unsigned int y;
    unsigned int width;
    unsigned int height;
    const char* text;
    int is_active;
    void (*on_click)(void);
} Widget;

Widget* widget_create(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* text);
void widget_draw(Widget* widget);
void widget_activate(Widget* widget);
void widget_handle_click(Widget* widget);
void widget_destroy(Widget* widget);

#endif