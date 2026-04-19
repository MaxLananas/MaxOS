#include "widget.h"
#include "ui.h"
#include "../drivers/screen.h"

Widget* widget_create(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* text) {
    Widget* widget = (Widget*)0x101000; // Simple allocation pour l'exemple
    widget->x = x;
    widget->y = y;
    widget->width = width;
    widget->height = height;
    widget->text = text;
    widget->is_active = 0;
    widget->on_click = 0;
    return widget;
}

void widget_draw(Widget* widget) {
    ui_draw_button(widget->x, widget->y, widget->width, widget->height, widget->text);
}

void widget_activate(Widget* widget) {
    widget->is_active = 1;
    widget_draw(widget);
}

void widget_handle_click(Widget* widget) {
    if (widget->on_click) {
        widget->on_click();
    }
}

void widget_destroy(Widget* widget) {
    // Simple implementation - no actual memory free
    widget->width = 0;
    widget->height = 0;
}